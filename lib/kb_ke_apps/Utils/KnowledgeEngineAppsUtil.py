import time
import json
import os
import errno
import uuid
import shutil

from kb_ke_util.kb_ke_utilClient import kb_ke_util
from DataFileUtil.DataFileUtilClient import DataFileUtil
from Workspace.WorkspaceClient import Workspace as Workspace
from KBaseReport.KBaseReportClient import KBaseReport
from SetAPI.SetAPIServiceClient import SetAPI

def log(message, prefix_newline=False):
    print(('\n' if prefix_newline else '') + str(time.time()) + ': ' + message)

class KnowledgeEngineAppsUtil:

    METRIC = ["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine", 
              "dice", "euclidean", "hamming", "jaccard", "kulsinski", "matching", 
              "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath", "sqeuclidean", 
              "yule"]

    METHOD = ["single", "complete", "average", "weighted", "centroid", "median", "ward"]

    CRITERION = ["inconsistent", "distance", "maxclust"]

    def _mkdir_p(self, path):
        """
        _mkdir_p: make directory for given path
        """
        if not path:
            return
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def _validate_run_expression_matrix_cluster_params(self, params):
        """
        _validate_run_expression_matrix_cluster_params:
                validates params passed to run_expression_matrix_cluster method
        """

        log('start validating run_expression_matrix_cluster params')

        # check for required parameters
        for p in ['expression_matrix_ref', 'workspace_name', 'feature_set_suffix', 
                  'dist_threshold']:
            if p not in params:
                raise ValueError('"{}" parameter is required, but missing'.format(p))

        # check metric validation
        metric = params.get('dist_metric')
        if metric and metric not in self.METRIC:
            error_msg = 'INPUT ERROR:\nInput metric function [{}] is not valid.\n'.format(metric)
            error_msg += 'Available metric: {}'.format(self.METRIC)
            raise ValueError(error_msg)

        # check method validation
        method = params.get('linkage_method')
        if method and method not in self.METHOD:
            error_msg = 'INPUT ERROR:\nInput linkage algorithm [{}] is not valid.\n'.format(method)
            error_msg += 'Available metric: {}'.format(self.METHOD)
            raise ValueError(error_msg)

        # check criterion validation
        criterion = params.get('fcluster_criterion')
        if criterion and criterion not in self.CRITERION:
            error_msg = 'INPUT ERROR:\nInput criterion [{}] is not valid.\n'.format(criterion)
            error_msg += 'Available metric: {}'.format(self.CRITERION)
            raise ValueError(error_msg)

    def _reverse_data_matrix(self, data_matrix):
        """
        _reverse_data_matrix: produce a reverse data matrix
        """
        row_ids = data_matrix['row_ids']
        values = data_matrix['values']
        col_ids = data_matrix['col_ids']
        
        reverse_data_matrix = dict()
        reverse_data_matrix.update({'row_ids': col_ids})
        reverse_data_matrix.update({'col_ids': row_ids})
        reverse_col_num = len(col_ids)
        reverse_values = [[] for i in range(reverse_col_num)]

        for value in values:
            for pos, element in enumerate(value):
                reverse_value = reverse_values[pos]
                reverse_value.append(element)

        reverse_data_matrix.update({'values': reverse_values})

        return reverse_data_matrix

    def _generate_feature_set(self, feature_ids, genome_id, workspace_name, feature_set_name):
        """
        _generate_feature_set: generate FeatureSet object
        KBaseCollections.FeatureSet type:
        typedef structure {
            string description;
            list<feature_id> element_ordering;
            mapping<feature_id, list<genome_ref>> elements;
        } FeatureSet;
        """

        log('start saving KBaseCollections.FeatureSet object')

        if isinstance(workspace_name, int) or workspace_name.isdigit():
            workspace_id = workspace_name
        else:
            workspace_id = self.dfu.ws_name_to_id(workspace_name)

        elements = {}
        map(lambda feature_id: elements.update({feature_id: [genome_id]}), feature_ids)
        feature_set_data = {'description': 'Generated FeatureSet from DifferentialExpression',
                            'element_ordering': feature_ids,
                            'elements': elements}

        object_type = 'KBaseCollections.FeatureSet'
        save_object_params = {
            'id': workspace_id,
            'objects': [{'type': object_type,
                         'data': feature_set_data,
                         'name': feature_set_name}]}

        dfu_oi = self.dfu.save_objects(save_object_params)[0]
        feature_set_obj_ref = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])

        return feature_set_obj_ref

    def _build_cluster_set(self, flat_cluster, cluster_set_name, genome_ref, workspace_name):
        """
        _build_cluster_set: build FeatureSetSet object
        """
        items = []
        for key, elements in flat_cluster.iteritems():
            cluster_name = cluster_set_name + '_' + key
            feature_set_obj_ref = self._generate_feature_set(elements, genome_ref, 
                                                             workspace_name, cluster_name)
            items.append({'ref': feature_set_obj_ref})

        featureset_set_data = {'description': 'FeatureSetSet by KnowledgeEngineApps', 
                               'items': items}
        featureset_set_save_params = {'data': featureset_set_data,
                                      'workspace': workspace_name,
                                      'output_object_name': cluster_set_name}

        save_result = self.set_client.save_feature_set_set_v1(featureset_set_save_params)
        featureset_set_ref = save_result['set_ref']

        return featureset_set_ref

    def _generate_visualization_content(self, output_directory, feature_dendrogram_path, 
                                        feature_dendrogram_truncate_path,
                                        condition_dendrogram_path,
                                        condition_dendrogram_truncate_path):
        """
        _generate_visualization_content: generate visualization html content
        """

        visualization_content = ''

        if feature_dendrogram_path:
            feature_dendrogram_name = 'feature_dendrogram.png'
            feature_dendrogram_display_name = 'feature dendrogram'

            shutil.copy2(feature_dendrogram_path,
                         os.path.join(output_directory, feature_dendrogram_name))

            visualization_content += '<div class="gallery">'
            visualization_content += '<a target="_blank" href="{}">'.format(feature_dendrogram_name)
            visualization_content += '<img src="{}" '.format(feature_dendrogram_name)
            visualization_content += 'alt="{}" width="600" height="400">'.format(feature_dendrogram_display_name)
            visualization_content += '</a><div class="desc">{}</div></div>'.format(feature_dendrogram_display_name)

        if feature_dendrogram_truncate_path:
            feature_den_truncate_name = 'feature_dendrogram_last12.png'
            feature_den_truncate_display_name = 'feature dendrogram truncated (last 12 merges)'

            shutil.copy2(feature_dendrogram_truncate_path,
                         os.path.join(output_directory, feature_den_truncate_name))

            visualization_content += '<div class="gallery">'
            visualization_content += '<a target="_blank" href="{}">'.format(feature_den_truncate_name)
            visualization_content += '<img src="{}" '.format(feature_den_truncate_name)
            visualization_content += 'alt="{}" width="600" height="400">'.format(feature_den_truncate_display_name)
            visualization_content += '</a><div class="desc">{}</div></div>'.format(feature_den_truncate_display_name)

        if condition_dendrogram_path:
            condition_dendrogram_name = 'condition_dendrogram.png'
            condition_dendrogram_display_name = 'condition dendrogram'

            shutil.copy2(condition_dendrogram_path,
                         os.path.join(output_directory, condition_dendrogram_name))

            visualization_content += '<div class="gallery">'
            visualization_content += '<a target="_blank" href="{}">'.format(condition_dendrogram_name)
            visualization_content += '<img src="{}" '.format(condition_dendrogram_name)
            visualization_content += 'alt="{}" width="600" height="400">'.format(condition_dendrogram_display_name)
            visualization_content += '</a><div class="desc">{}</div></div>'.format(condition_dendrogram_display_name)

        if condition_dendrogram_truncate_path:
            condition_den_truncate_name = 'condition_dendrogram_last12.png'
            condition_den_truncate_display_name = 'condition dendrogram truncated (last 12 merges)'

            shutil.copy2(condition_dendrogram_truncate_path,
                         os.path.join(output_directory, condition_den_truncate_name))

            visualization_content += '<div class="gallery">'
            visualization_content += '<a target="_blank" href="{}">'.format(condition_den_truncate_name)
            visualization_content += '<img src="{}" '.format(condition_den_truncate_name)
            visualization_content += 'alt="{}" width="600" height="400">'.format(condition_den_truncate_display_name)
            visualization_content += '</a><div class="desc">{}</div></div>'.format(condition_den_truncate_display_name)

        if not visualization_content:
            visualization_content = '<p>Dendrogram is too large to be printed.</p>'

        return visualization_content

    def _generate_html_report(self, feature_set_set_refs, feature_dendrogram_path,
                              feature_dendrogram_truncate_path, condition_dendrogram_path,
                              condition_dendrogram_truncate_path):
        """
        _generate_html_report: generate html summary report
        """

        log('start generating html report')
        html_report = list()

        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(output_directory)
        result_file_path = os.path.join(output_directory, 'report.html')

        visualization_content = self._generate_visualization_content(
                                                            output_directory,
                                                            feature_dendrogram_path, 
                                                            feature_dendrogram_truncate_path,
                                                            condition_dendrogram_path,
                                                            condition_dendrogram_truncate_path)

        overview_content = ''
        for feature_set_set_ref in feature_set_set_refs:
          
            feature_set_set_obj = self.ws.get_objects2({'objects':
                                                        [{'ref': 
                                                         feature_set_set_ref}]})['data'][0]
            feature_set_set_data = feature_set_set_obj['data']
            feature_set_set_info = feature_set_set_obj['info']

            feature_set_set_name = feature_set_set_info[1]

            items = feature_set_set_data['items']

            if '_condition' in feature_set_set_name:
                overview_content += '<p><br/></p>'
                overview_content += '<br/><table><tr><th>Generated Condition Cluster Set'
                overview_content += '</th></tr>'
                overview_content += '<tr><td>{} ({})'.format(feature_set_set_name,
                                                             feature_set_set_ref)
                overview_content += '</td></tr></table>'

                overview_content += '<p><br/></p>'

                overview_content += '<br/><table><tr><th>Generated Condition Cluster'
                overview_content += '</th><th></th><th></th><th></th></tr>'
                overview_content += '<tr><th>Cluster Name</th>'
                overview_content += '<th>Condition Count</th>'
                overview_content += '</tr>'
                for item in items:
                    feature_set_ref = item['ref']
                    feature_set_object = self.ws.get_objects2({'objects':
                                                               [{'ref': 
                                                                feature_set_ref}]})['data'][0]

                    feature_set_data = feature_set_object['data']
                    feature_set_info = feature_set_object['info']
                    feature_set_name = feature_set_info[1]
                    number_features = len(feature_set_data['element_ordering'])

                    overview_content += '<tr><td>{} ({})</td>'.format(feature_set_name, 
                                                                      feature_set_ref)
                    overview_content += '<td>{}</td></tr>'.format(number_features)
                overview_content += '</table>'
            else:
                overview_content += '<p><br/></p>'
                overview_content += '<br/><table><tr><th>Generated Feature Cluster Set'
                overview_content += '</th></tr>'
                overview_content += '<tr><td>{} ({})'.format(feature_set_set_name,
                                                             feature_set_set_ref)
                overview_content += '</td></tr></table>'

                overview_content += '<p><br/></p>'

                overview_content += '<br/><table><tr><th>Generated Feature Clusters'
                overview_content += '</th><th></th><th></th><th></th></tr>'
                overview_content += '<tr><th>Cluster Name</th>'
                overview_content += '<th>Feature Count</th>'
                overview_content += '</tr>'
                for item in items:
                    feature_set_ref = item['ref']
                    feature_set_object = self.ws.get_objects2({'objects':
                                                               [{'ref': 
                                                                feature_set_ref}]})['data'][0]

                    feature_set_data = feature_set_object['data']
                    feature_set_info = feature_set_object['info']
                    feature_set_name = feature_set_info[1]
                    number_features = len(feature_set_data['element_ordering'])

                    overview_content += '<tr><td>{} ({})</td>'.format(feature_set_name, 
                                                                      feature_set_ref)
                    overview_content += '<td>{}</td></tr>'.format(number_features)
                overview_content += '</table>'

        with open(result_file_path, 'w') as result_file:
            with open(os.path.join(os.path.dirname(__file__), 'report_template.html'),
                      'r') as report_template_file:
                report_template = report_template_file.read()
                report_template = report_template.replace('<p>Overview_Content</p>',
                                                          overview_content)
                report_template = report_template.replace('<p>Visualization_Content</p>',
                                                          visualization_content)
                result_file.write(report_template)

        report_shock_id = self.dfu.file_to_shock({'file_path': output_directory,
                                                  'pack': 'zip'})['shock_id']

        html_report.append({'shock_id': report_shock_id,
                            'name': os.path.basename(result_file_path),
                            'label': os.path.basename(result_file_path),
                            'description': 'HTML summary report for ExpressionMatrix Cluster App'})
        return html_report

    def _generate_report(self, feature_set_set_refs, workspace_name, feature_dendrogram_path,
                         feature_dendrogram_truncate_path, condition_dendrogram_path,
                         condition_dendrogram_truncate_path):
        """
        _generate_report: generate summary report
        """

        log('creating report')

        output_html_files = self._generate_html_report(feature_set_set_refs,
                                                       feature_dendrogram_path,
                                                       feature_dendrogram_truncate_path,
                                                       condition_dendrogram_path,
                                                       condition_dendrogram_truncate_path)

        objects_created = []
        for feature_set_set_ref in feature_set_set_refs:

            feature_set_set_data = self.ws.get_objects2({'objects':
                                                        [{'ref': 
                                                         feature_set_set_ref}]})['data'][0]['data']

            items = feature_set_set_data['items']

            description_set = 'Cluster Set'
            description_object = 'Cluster'
            objects_created.append({'ref': feature_set_set_ref,
                                    'description': description_set})

            for item in items:
                feature_set_ref = item['ref']
                objects_created.append({'ref': feature_set_ref,
                                        'description': description_object})

        report_params = {'message': '',
                         'workspace_name': workspace_name,
                         'objects_created': objects_created,
                         'html_links': output_html_files,
                         'direct_html_link_index': 0,
                         'html_window_height': 333,
                         'report_object_name': 'kb_deseq2_report_' + str(uuid.uuid4())}

        kbase_report_client = KBaseReport(self.callback_url)
        output = kbase_report_client.create_extended_report(report_params)

        report_output = {'report_name': output['name'], 'report_ref': output['ref']}

        return report_output

    def _build_flat_cluster(self, data_matrix, dist_threshold, 
                            dist_metric=None, linkage_method=None, fcluster_criterion=None):
        """
        _build_cluster: build flat clusters and dendrogram for data_matrix
        """

        # calculate distance matrix
        pdist_params = {'data_matrix': data_matrix,
                        'metric': dist_metric}
        pdist_ret = self.ke_util.run_pdist(pdist_params)

        square_dist_matrix = pdist_ret['square_dist_matrix']
        labels = pdist_ret['labels']

        # performs hierarchical/agglomerative clustering
        linkage_params = {'square_dist_matrix': square_dist_matrix,
                          'method': linkage_method}
        linkage_ret = self.ke_util.run_linkage(linkage_params)

        linkage_matrix = linkage_ret['linkage_matrix']

        merges = len(linkage_matrix)

        # generate flat clusters
        fcluster_params = {'linkage_matrix': linkage_matrix,
                           'dist_threshold': dist_threshold,
                           'labels': labels,
                           'criterion': fcluster_criterion}
        fcluster_ret = self.ke_util.run_fcluster(fcluster_params)

        flat_cluster = fcluster_ret['flat_cluster']

        # generate dendrogram
        if len(linkage_matrix) < 1500:
            dendrogram_params = {'linkage_matrix': linkage_matrix,
                                 'dist_threshold': dist_threshold,
                                 'labels': labels}

            dendrogram_ret = self.ke_util.run_dendrogram(dendrogram_params)

            dendrogram_path = dendrogram_ret['result_plots'][0]

            # generate truncated (last 12 merges) dendrogram
            if merges > 24:
                dendrogram_truncate_params = {'linkage_matrix': linkage_matrix,
                                              'dist_threshold': dist_threshold,
                                              'labels': labels,
                                              'last_merges': 12}
                dendrogram_truncate_ret = self.ke_util.run_dendrogram(dendrogram_truncate_params)

                dendrogram_truncate_path = dendrogram_truncate_ret['result_plots'][0]
            else:
                dendrogram_truncate_path = None
        else:
            dendrogram_path = None
            dendrogram_truncate_path = None

        return flat_cluster, dendrogram_path, dendrogram_truncate_path

    def __init__(self, config):
        self.ws_url = config["workspace-url"]
        self.callback_url = config['SDK_CALLBACK_URL']
        self.token = config['KB_AUTH_TOKEN']
        self.shock_url = config['shock-url']
        self.srv_wiz_url = config['srv-wiz-url']
        self.scratch = config['scratch']
        self.dfu = DataFileUtil(self.callback_url)
        self.ke_util = kb_ke_util(self.callback_url, service_ver='dev')
        self.ws = Workspace(self.ws_url, token=self.token)
        self.set_client = SetAPI(self.srv_wiz_url)

    def run_expression_matrix_cluster(self, params):
        """
        run_expression_matrix_cluster: generates clusters for ExpressionMatrix data object

        expression_matrix_ref: ExpressionMatrix object reference
        workspace_name: the name of the workspace
        feature_set_suffix: suffix append to FeatureSet object name
        dist_threshold: the threshold to apply when forming flat clusters

        Optional arguments:
        dist_metric: The distance metric to use. Default set to 'euclidean'.
                     The distance function can be
                     ["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine", 
                      "dice", "euclidean", "hamming", "jaccard", "kulsinski", "matching", 
                      "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath", 
                      "sqeuclidean", "yule"]
                     Details refer to:
                     https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html

        linkage_method: The linkage algorithm to use. Default set to 'ward'.
                        The method can be
                        ["single", "complete", "average", "weighted", "centroid", "median", "ward"]
                        Details refer to:
                        https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html

        fcluster_criterion: The criterion to use in forming flat clusters. 
                            Default set to 'inconsistent'.
                            The criterion can be
                            ["inconsistent", "distance", "maxclust"]
                            Details refer to:
                            https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.fcluster.html

        return:
        feature_set_set_refs: a list of result FeatureSetSet object references
        report_name: report name generated by KBaseReport
        report_ref: report reference generated by KBaseReport
        """
        log('--->\nrunning run_expression_matrix_cluster\n' +
            'params:\n{}'.format(json.dumps(params, indent=1)))

        self._validate_run_expression_matrix_cluster_params(params)

        expression_matrix_ref = params.get('expression_matrix_ref')
        workspace_name = params.get('workspace_name')
        feature_set_suffix = params.get('feature_set_suffix')
        dist_threshold = params.get('dist_threshold')
        dist_metric = params.get('dist_metric')
        linkage_method = params.get('linkage_method')
        fcluster_criterion = params.get('fcluster_criterion')

        expression_matrix_object = self.ws.get_objects2({'objects': 
                                                        [{'ref': 
                                                          expression_matrix_ref}]})['data'][0]
        expression_matrix_info = expression_matrix_object['info']
        expression_matrix_data = expression_matrix_object['data']
        expression_matrix_data_matrix = expression_matrix_data['data']

        feature_data_matrix = expression_matrix_data_matrix
        condition_data_matrix = self._reverse_data_matrix(expression_matrix_data_matrix)

        (feature_flat_cluster,
         feature_dendrogram_path,
         feature_dendrogram_truncate_path) = self._build_flat_cluster(
                                                            feature_data_matrix,
                                                            dist_threshold,
                                                            dist_metric=dist_metric,
                                                            linkage_method=linkage_method,
                                                            fcluster_criterion=fcluster_criterion)

        (condition_flat_cluster,
         condition_dendrogram_path,
         condition_dendrogram_truncate_path) = self._build_flat_cluster(
                                                            condition_data_matrix, 
                                                            dist_threshold, 
                                                            dist_metric=dist_metric,
                                                            linkage_method=linkage_method,
                                                            fcluster_criterion=fcluster_criterion)

        genome_ref = expression_matrix_data.get('genome_ref')
        expression_matrix_name = expression_matrix_info[1]
        feature_set_set_refs = []

        feature_cluster_set_name = expression_matrix_name + '_feature' + feature_set_suffix
        feature_feature_set = self._build_cluster_set(feature_flat_cluster,
                                                      feature_cluster_set_name,
                                                      genome_ref,
                                                      workspace_name)
        feature_set_set_refs.append(feature_feature_set)

        condition_cluster_set_name = expression_matrix_name + '_condition' + feature_set_suffix
        condition_feature_set = self._build_cluster_set(condition_flat_cluster,
                                                        condition_cluster_set_name,
                                                        genome_ref,
                                                        workspace_name)
        feature_set_set_refs.append(condition_feature_set)

        returnVal = {'feature_set_set_refs': feature_set_set_refs}

        report_output = self._generate_report(feature_set_set_refs,
                                              workspace_name,
                                              feature_dendrogram_path,
                                              feature_dendrogram_truncate_path,
                                              condition_dendrogram_path,
                                              condition_dendrogram_truncate_path)
        returnVal.update(report_output)

        return returnVal
