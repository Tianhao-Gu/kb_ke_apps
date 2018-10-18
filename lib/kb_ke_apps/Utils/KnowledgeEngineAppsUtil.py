import time
import json
import os
import errno
import uuid
import shutil
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import itertools
import seaborn as sns
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly.offline import plot
import scipy.cluster.hierarchy as hier

from kb_ke_util.kb_ke_utilClient import kb_ke_util
from DataFileUtil.DataFileUtilClient import DataFileUtil
from Workspace.WorkspaceClient import Workspace as Workspace
from KBaseReport.KBaseReportClient import KBaseReport
from SetAPI.SetAPIServiceClient import SetAPI
from GenericsAPI.GenericsAPIClient import GenericsAPI


def log(message, prefix_newline=False):
    print((('\n' if prefix_newline else '') + str(time.time()) + ': ' + message))


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

    def _validate_run_pca_params(self, params):
        """
        _validate_run_pca_params:
            validates params passed to run_pca method
        """

        log('start validating run_pca params')

        # check for required parameters
        for p in ['cluster_set_ref', 'workspace_name', 'pca_matrix_name']:
            if p not in params:
                raise ValueError('"{}" parameter is required, but missing'.format(p))

    def _validate_run_kmeans_cluster_params(self, params):
        """
        _validate_run_kmeans_cluster_params:
                validates params passed to run_kmeans_cluster method
        """

        log('start validating run_kmeans_cluster params')

        # check for required parameters
        for p in ['matrix_ref', 'workspace_name', 'cluster_set_name',
                  'k_num']:
            if p not in params:
                raise ValueError('"{}" parameter is required, but missing'.format(p))

        # check metric validation
        metric = params.get('dist_metric')
        if metric and metric not in self.METRIC:
            error_msg = 'INPUT ERROR:\nInput metric function [{}] is not valid.\n'.format(metric)
            error_msg += 'Available metric: {}'.format(self.METRIC)
            raise ValueError(error_msg)

    def _validate_run_hierarchical_cluster_params(self, params):
        """
        _validate_run_hierarchical_cluster_params:
                validates params passed to run_hierarchical_cluster method
        """

        log('start validating run_hierarchical_cluster params')

        # check for required parameters
        for p in ['matrix_ref', 'workspace_name', 'cluster_set_name']:
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
            error_msg = 'INPUT ERROR:\nInput linkage algorithm [{}] is not valid.\n'.format(
                                                                                        method)
            error_msg += 'Available metric: {}'.format(self.METHOD)
            raise ValueError(error_msg)

        # check criterion validation
        criterion = params.get('fcluster_criterion')
        if criterion and criterion not in self.CRITERION:
            error_msg = 'INPUT ERROR:\nInput criterion [{}] is not valid.\n'.format(criterion)
            error_msg += 'Available metric: {}'.format(self.CRITERION)
            raise ValueError(error_msg)

    def _gen_clusters(self, clusters, conditionset_mapping):
        clusters_list = list()

        for cluster in list(clusters.values()):
            labeled_cluster = {}
            labeled_cluster.update({'id_to_data_position': cluster})
            if conditionset_mapping:
                id_to_condition = {k: v for k, v in list(conditionset_mapping.items()) if k in list(cluster.keys())}
                labeled_cluster.update({'id_to_condition': id_to_condition})

            clusters_list.append(labeled_cluster)

        return clusters_list

    def _gen_hierarchical_clusters(self, clusters, conditionset_mapping, data_matrix):
        clusters_list = list()

        df = pd.read_json(data_matrix)
        index = df.index.tolist()

        for cluster in list(clusters.values()):
            labeled_cluster = {}
            id_to_data_position = {}
            for item in cluster:
                id_to_data_position.update({item: index.index(item)})

            labeled_cluster.update({'id_to_data_position': id_to_data_position})
            if conditionset_mapping:
                id_to_condition = {k: v for k, v in list(conditionset_mapping.items()) if k in cluster}
                labeled_cluster.update({'id_to_condition': id_to_condition})

            clusters_list.append(labeled_cluster)

        return clusters_list

    def _build_hierarchical_cluster_set(self, clusters, cluster_set_name, genome_ref, matrix_ref,
                                        conditionset_mapping, conditionset_ref, workspace_name,
                                        clustering_parameters, data_matrix):

        """
        _build_kmeans_cluster_set: build KBaseExperiments.ClusterSet object
        """

        log('start saving KBaseExperiments.ClusterSet object')

        if isinstance(workspace_name, int) or workspace_name.isdigit():
            workspace_id = workspace_name
        else:
            workspace_id = self.dfu.ws_name_to_id(workspace_name)

        clusters_list = self._gen_hierarchical_clusters(clusters, conditionset_mapping,
                                                        data_matrix)

        cluster_set_data = {'clusters': clusters_list,
                            'clustering_parameters': clustering_parameters,
                            'original_data': matrix_ref,
                            'condition_set_ref': conditionset_ref,
                            'genome_ref': genome_ref}

        cluster_set_data = {k: v for k, v in list(cluster_set_data.items()) if v}

        object_type = 'KBaseExperiments.ClusterSet'
        save_object_params = {
            'id': workspace_id,
            'objects': [{'type': object_type,
                         'data': cluster_set_data,
                         'name': cluster_set_name}]}

        dfu_oi = self.dfu.save_objects(save_object_params)[0]
        cluster_set_ref = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])

        return cluster_set_ref

    def _build_kmeans_cluster_set(self, clusters, cluster_set_name, genome_ref, matrix_ref,
                                  conditionset_mapping, conditionset_ref, workspace_name,
                                  clustering_parameters):
        """
        _build_kmeans_cluster_set: build KBaseExperiments.ClusterSet object
        """

        log('start saving KBaseExperiments.ClusterSet object')

        if isinstance(workspace_name, int) or workspace_name.isdigit():
            workspace_id = workspace_name
        else:
            workspace_id = self.dfu.ws_name_to_id(workspace_name)

        clusters_list = self._gen_clusters(clusters, conditionset_mapping)

        cluster_set_data = {'clusters': clusters_list,
                            'clustering_parameters': clustering_parameters,
                            'original_data': matrix_ref,
                            'condition_set_ref': conditionset_ref,
                            'genome_ref': genome_ref}

        cluster_set_data = {k: v for k, v in list(cluster_set_data.items()) if v}

        object_type = 'KBaseExperiments.ClusterSet'
        save_object_params = {
            'id': workspace_id,
            'objects': [{'type': object_type,
                         'data': cluster_set_data,
                         'name': cluster_set_name}]}

        dfu_oi = self.dfu.save_objects(save_object_params)[0]
        cluster_set_ref = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])

        return cluster_set_ref

    def _generate_visualization_content(self, output_directory,
                                        row_dendrogram_path,
                                        row_dendrogram_truncate_path,
                                        col_dendrogram_path,
                                        col_dendrogram_truncate_path,
                                        clusterheatmap):

        """
        _generate_visualization_content: generate visualization html content
        """

        clusterheatmap_content = ''
        row_dendrogram_content = ''
        col_dendrogram_content = ''

        if os.path.basename(clusterheatmap).endswith('.png'):
            clusterheatmap_name = 'clusterheatmap.png'
            clusterheatmap_display_name = 'cluster heatmap'

            shutil.copy2(clusterheatmap,
                         os.path.join(output_directory, clusterheatmap_name))

            clusterheatmap_content += '<div class="gallery">'
            clusterheatmap_content += '<a target="_blank" href="{}">'.format(
                                                                        clusterheatmap_name)
            clusterheatmap_content += '<img src="{}" '.format(clusterheatmap_name)
            clusterheatmap_content += 'alt="{}" width="1000" height="1000">'.format(
                                                                clusterheatmap_display_name)
            clusterheatmap_content += '</a><div class="desc">{}</div></div>'.format(
                                                                clusterheatmap_display_name)
        elif os.path.basename(clusterheatmap).endswith('.html'):
            clusterheatmap_html = 'clusterheatmap.html'
            shutil.copy2(clusterheatmap,
                         os.path.join(output_directory, clusterheatmap_html))

            clusterheatmap_content += '<iframe height="900px" width="100%" '
            clusterheatmap_content += 'src="{}" style="border:none;"></iframe>'.format(clusterheatmap_html)
        else:
            raise ValueError('Unexpected cluster heatmap file format')

        if row_dendrogram_path:
            row_dendrogram_name = 'row_dendrogram.png'
            row_dendrogram_display_name = 'row dendrogram'

            shutil.copy2(row_dendrogram_path,
                         os.path.join(output_directory, row_dendrogram_name))

            row_dendrogram_content += '<div class="gallery">'
            row_dendrogram_content += '<a target="_blank" href="{}">'.format(
                                                                        row_dendrogram_name)
            row_dendrogram_content += '<img src="{}" '.format(row_dendrogram_name)
            row_dendrogram_content += 'alt="{}" width="1000" height="800">'.format(
                                                                row_dendrogram_display_name)
            row_dendrogram_content += '</a><div class="desc">{}</div></div>'.format(
                                                                row_dendrogram_display_name)

        if row_dendrogram_truncate_path:
            row_den_truncate_name = 'row_dendrogram_last12.png'
            row_den_truncate_display_name = 'row dendrogram truncated (last 12 merges)'

            shutil.copy2(row_dendrogram_truncate_path,
                         os.path.join(output_directory, row_den_truncate_name))

            row_dendrogram_content += '<div class="gallery">'
            row_dendrogram_content += '<a target="_blank" href="{}">'.format(
                                                                        row_den_truncate_name)
            row_dendrogram_content += '<img src="{}" '.format(row_den_truncate_name)
            row_dendrogram_content += 'alt="{}" width="1000" height="800">'.format(
                                                                row_den_truncate_display_name)
            row_dendrogram_content += '</a><div class="desc">{}</div></div>'.format(
                                                                row_den_truncate_display_name)

        if col_dendrogram_path:
            col_dendrogram_name = 'column_dendrogram.png'
            col_dendrogram_display_name = 'column dendrogram'

            shutil.copy2(col_dendrogram_path,
                         os.path.join(output_directory, col_dendrogram_name))

            col_dendrogram_content += '<div class="gallery">'
            col_dendrogram_content += '<a target="_blank" href="{}">'.format(
                                                                        col_dendrogram_name)
            col_dendrogram_content += '<img src="{}" '.format(col_dendrogram_name)
            col_dendrogram_content += 'alt="{}" width="1000" height="800">'.format(
                                                                col_dendrogram_display_name)
            col_dendrogram_content += '</a><div class="desc">{}</div></div>'.format(
                                                                col_dendrogram_display_name)

        if col_dendrogram_truncate_path:
            col_den_truncate_name = 'column_dendrogram_last12.png'
            col_den_truncate_display_name = 'column dendrogram truncated (last 12 merges)'

            shutil.copy2(col_dendrogram_truncate_path,
                         os.path.join(output_directory, col_den_truncate_name))

            col_dendrogram_content += '<div class="gallery">'
            col_dendrogram_content += '<a target="_blank" href="{}">'.format(
                                                                    col_den_truncate_name)
            col_dendrogram_content += '<img src="{}" '.format(col_den_truncate_name)
            col_dendrogram_content += 'alt="{}" width="1000" height="800">'.format(
                                                            col_den_truncate_display_name)
            col_dendrogram_content += '</a><div class="desc">{}</div></div>'.format(
                                                            col_den_truncate_display_name)

        return clusterheatmap_content, row_dendrogram_content, col_dendrogram_content

    def _generate_hierarchical_html_report(self, cluster_set_refs,
                                           row_dendrogram_path,
                                           row_dendrogram_truncate_path,
                                           col_dendrogram_path,
                                           col_dendrogram_truncate_path,
                                           clusterheatmap):
        """
        _generate_hierarchical_html_report: generate html summary report for hierarchical
                                            clustering app
        """

        log('start generating html report')
        html_report = list()

        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(output_directory)
        result_file_path = os.path.join(output_directory, 'hier_report.html')

        (clusterheatmap_content,
         row_dendrogram_content,
         col_dendrogram_content) = self._generate_visualization_content(
                                                            output_directory,
                                                            row_dendrogram_path,
                                                            row_dendrogram_truncate_path,
                                                            col_dendrogram_path,
                                                            col_dendrogram_truncate_path,
                                                            clusterheatmap)

        with open(result_file_path, 'w') as result_file:
            with open(os.path.join(os.path.dirname(__file__), 'hier_report_template.html'),
                      'r') as report_template_file:
                report_template = report_template_file.read()
                report_template = report_template.replace('<p>ClusterHeatmap</p>',
                                                          clusterheatmap_content)
                report_template = report_template.replace('<p>Row_Dendrogram</p>',
                                                          row_dendrogram_content)
                report_template = report_template.replace('<p>Column_Dendrogram</p>',
                                                          col_dendrogram_content)
                result_file.write(report_template)

        report_shock_id = self.dfu.file_to_shock({'file_path': output_directory,
                                                  'pack': 'zip'})['shock_id']

        html_report.append({'shock_id': report_shock_id,
                            'name': os.path.basename(result_file_path),
                            'label': os.path.basename(result_file_path),
                            'description': 'HTML summary report for ExpressionMatrix Cluster App'
                            })
        return html_report

    def _generate_hierarchical_cluster_report(self, cluster_set_refs, workspace_name,
                                              row_dendrogram_path,
                                              row_dendrogram_truncate_path,
                                              col_dendrogram_path,
                                              col_dendrogram_truncate_path,
                                              clusterheatmap):
        """
        _generate_hierarchical_cluster_report: generate summary report
        """

        log('creating report')

        output_html_files = self._generate_hierarchical_html_report(
                                                        cluster_set_refs,
                                                        row_dendrogram_path,
                                                        row_dendrogram_truncate_path,
                                                        col_dendrogram_path,
                                                        col_dendrogram_truncate_path,
                                                        clusterheatmap)

        objects_created = []
        for cluster_set_ref in cluster_set_refs:
            objects_created.append({'ref': cluster_set_ref,
                                    'description': 'Hierarchical ClusterSet'})

        report_params = {'message': '',
                         'workspace_name': workspace_name,
                         'objects_created': objects_created,
                         'html_links': output_html_files,
                         'direct_html_link_index': 0,
                         'html_window_height': 333,
                         'report_object_name': 'kb_hier_cluster_report_' + str(uuid.uuid4())}

        kbase_report_client = KBaseReport(self.callback_url)
        output = kbase_report_client.create_extended_report(report_params)

        report_output = {'report_name': output['name'], 'report_ref': output['ref']}

        return report_output

    def _generate_kmeans_cluster_report(self, cluster_set_refs, workspace_name):
        """
        _generate_kmeans_cluster_report: generate summary report
        """
        objects_created = []
        for cluster_set_ref in cluster_set_refs:
            objects_created.append({'ref': cluster_set_ref,
                                    'description': 'Kmeans ClusterSet'})
        report_params = {'message': '',
                         'objects_created': objects_created,
                         'workspace_name': workspace_name,
                         'report_object_name': 'run_kmeans_cluster_' + str(uuid.uuid4())}

        kbase_report_client = KBaseReport(self.callback_url, token=self.token)
        output = kbase_report_client.create_extended_report(report_params)

        report_output = {'report_name': output['name'], 'report_ref': output['ref']}

        return report_output

    def _generate_pca_html_files(self, pca_plots, n_components):

        log('start generating html report')
        html_report = list()

        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(output_directory)
        result_file_path = os.path.join(output_directory, 'pca_report.html')

        visualization_content = ''

        for pca_plot in pca_plots:
            pca_plot_name = os.path.basename(pca_plot)
            pca_plot_display_name = '{} Component PCA'.format(n_components)

            shutil.copy2(pca_plot,
                         os.path.join(output_directory, pca_plot_name))

            visualization_content += '<div class="gallery">'
            visualization_content += '<a target="_blank" href="{}">'.format(pca_plot_name)
            visualization_content += '<img src="{}" '.format(pca_plot_name)
            visualization_content += 'alt="{}" width="600" height="600">'.format(
                                                                    pca_plot_display_name)
            visualization_content += '</a><div class="desc">{}</div></div>'.format(
                                                                    pca_plot_display_name)

        with open(result_file_path, 'w') as result_file:
            with open(os.path.join(os.path.dirname(__file__), 'pca_report_template.html'),
                      'r') as report_template_file:
                report_template = report_template_file.read()
                report_template = report_template.replace('<p>Visualization_Content</p>',
                                                          visualization_content)
                result_file.write(report_template)

        report_shock_id = self.dfu.file_to_shock({'file_path': output_directory,
                                                  'pack': 'zip'})['shock_id']

        html_report.append({'shock_id': report_shock_id,
                            'name': os.path.basename(result_file_path),
                            'label': os.path.basename(result_file_path),
                            'description': 'HTML summary report for ExpressionMatrix Cluster App'
                            })
        return html_report

    def _generate_pca_plot(self, pca_matrix_data):
        """
        _generate_pca_plot: generate a plot for PCA data
        """
        pca_plots = []
        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(output_directory)

        df = pd.DataFrame(pca_matrix_data.get('values'),
                          index=pca_matrix_data.get('row_ids'),
                          columns=pca_matrix_data.get('col_ids'))

        n_components = list(range(1, df.columns.size))
        all_pairs = list(itertools.combinations(n_components, 2))

        for pair in all_pairs:
            first_component = pair[0]
            second_component = pair[1]
            pca_plot = os.path.join(output_directory, 'pca_{}_{}.png'.format(first_component,
                                                                             second_component))

            plt.switch_backend('agg')

            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(1, 1, 1)
            ax.set_xlabel('Principal Component {}'.format(first_component), fontsize=15)
            ax.set_ylabel('Principal Component {}'.format(second_component), fontsize=15)
            ax.set_title('{} component PCA'.format(len(n_components)), fontsize=20)

            clusters = list(set(['cluster_{}'.format(x) for x in df['cluster'].tolist()]))
            colors = ['red', 'green', 'blue', 'orange', 'yellow', 'pink', 'lightcyan', 'cyan']
            if len(clusters) > len(colors):
                np.random.seed(19680801)
                N = len(clusters)
                colors = []
                for i in range(N):
                    colors.append(np.random.rand(3,))

            for cluster, color in zip(clusters, colors):
                indicesToKeep = df['cluster'] == int(cluster.split('_')[-1])
                ax.scatter(df.loc[indicesToKeep, 'principal_component_{}'.format(first_component)],
                           df.loc[indicesToKeep, 'principal_component_{}'.format(second_component)],
                           c=color,
                           s=50)
            ax.legend(clusters, loc='best')
            ax.grid()

            plt.savefig(pca_plot)

            pca_plots.append(pca_plot)

        return pca_plots, len(n_components)

    def _generate_pca_report(self, pca_ref, pca_matrix_data, workspace_name):
        """
        _generate_kmeans_cluster_report: generate summary report
        """
        objects_created = []
        objects_created.append({'ref': pca_ref,
                                'description': 'PCA Matrix'})

        pca_plots, n_components = self._generate_pca_plot(pca_matrix_data)
        output_html_files = self._generate_pca_html_files(pca_plots, n_components)
        report_params = {'message': '',
                         'objects_created': objects_created,
                         'workspace_name': workspace_name,
                         'html_links': output_html_files,
                         'direct_html_link_index': 0,
                         'report_object_name': 'run_pca_' + str(uuid.uuid4())}

        kbase_report_client = KBaseReport(self.callback_url, token=self.token)
        output = kbase_report_client.create_extended_report(report_params)

        report_output = {'report_name': output['name'], 'report_ref': output['ref']}

        return report_output

    def _save_2D_matrix(self, df, clusters, workspace_name, pca_matrix_name):
        """
        _save_2D_matrix: save dataframe as KBaseFeatureValues.FloatMatrix2D object
        """

        log('start saving KBaseFeatureValues.FloatMatrix2D object')

        if isinstance(workspace_name, int) or workspace_name.isdigit():
            workspace_id = workspace_name
        else:
            workspace_id = self.dfu.ws_name_to_id(workspace_name)

        row_ids = df.index.tolist()
        col_ids = df.columns.tolist()
        col_ids.append('cluster')
        values = df.values.tolist()

        idx = 0
        for cluster in clusters:
            cluster_items = list(cluster.get('id_to_data_position').keys())

            for cluster_item in cluster_items:
                pos = row_ids.index(cluster_item)
                values[pos].append(idx)

            idx += 1

        pca_matrix_data = {'row_ids': row_ids,
                           'col_ids': col_ids,
                           'values': values}

        object_type = 'KBaseFeatureValues.FloatMatrix2D'
        save_object_params = {
            'id': workspace_id,
            'objects': [{'type': object_type,
                         'data': pca_matrix_data,
                         'name': pca_matrix_name}]}

        dfu_oi = self.dfu.save_objects(save_object_params)[0]
        float_matrix_ref = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])

        return float_matrix_ref, pca_matrix_data

    def _build_flat_cluster(self, data_matrix, dist_cutoff_rate,
                            dist_metric=None, linkage_method=None, fcluster_criterion=None):
        """
        _build_cluster: build flat clusters and dendrogram for data_matrix
        """

        log('start building clusters')
        # calculate distance matrix
        log('calculating distance matrix')
        pdist_params = {'data_matrix': data_matrix,
                        'metric': dist_metric}
        pdist_ret = self.ke_util.run_pdist(pdist_params)

        dist_matrix = pdist_ret['dist_matrix']
        labels = pdist_ret['labels']

        # performs hierarchical/agglomerative clustering
        log('performing hierarchical/agglomerative clustering')
        linkage_params = {'dist_matrix': dist_matrix,
                          'method': linkage_method}
        linkage_ret = self.ke_util.run_linkage(linkage_params)

        linkage_matrix = linkage_ret['linkage_matrix']

        newick = self.ke_util.linkage_2_newick({'linkage_matrix': linkage_matrix,
                                                'labels': labels})['newick']

        height = max([item[2] for item in linkage_matrix])
        dist_threshold = height * dist_cutoff_rate
        log('Height: {} Setting dist_threshold: {}'.format(height, dist_threshold))
        merges = len(linkage_matrix)

        # generate flat clusters
        fcluster_params = {'linkage_matrix': linkage_matrix,
                           'dist_threshold': dist_threshold,
                           'labels': labels,
                           'criterion': fcluster_criterion}
        fcluster_ret = self.ke_util.run_fcluster(fcluster_params)

        flat_cluster = fcluster_ret['flat_cluster']

        # generate dendrogram
        try:
            log('creating dendrogram')
            dendrogram_params = {'linkage_matrix': linkage_matrix,
                                 'dist_threshold': dist_threshold,
                                 'labels': labels}

            dendrogram_ret = self.ke_util.run_dendrogram(dendrogram_params)

            dendrogram_path = dendrogram_ret['result_plots'][0]
        except:
            dendrogram_path = None

        # generate truncated (last 12 merges) dendrogram
        if merges > 256:
            log('creating truncated dendrogram')
            dendrogram_truncate_params = {'linkage_matrix': linkage_matrix,
                                          'dist_threshold': dist_threshold,
                                          'labels': labels,
                                          'last_merges': 12}
            dendrogram_truncate_ret = self.ke_util.run_dendrogram(dendrogram_truncate_params)

            dendrogram_truncate_path = dendrogram_truncate_ret['result_plots'][0]
        else:
            dendrogram_truncate_path = None

        return flat_cluster, labels, newick, dendrogram_path, dendrogram_truncate_path

    def _build_kmeans_cluster(self, data_matrix, k_num, dist_metric=None):
        """
        _build_kmeans_cluster: Build Kmeans cluster
        """

        log('start building clusters')

        # calculate distance matrix
        log('calculating distance matrix')
        pdist_params = {'data_matrix': data_matrix,
                        'metric': dist_metric}
        pdist_ret = self.ke_util.run_pdist(pdist_params)

        dist_matrix = pdist_ret['dist_matrix']
        labels = pdist_ret['labels']

        # run kmeans algorithm
        log('performing kmeans algorithm')
        kmeans_params = {'dist_matrix': dist_matrix,
                         'k_num': k_num}
        kmeans_ret = self.ke_util.run_kmeans2(kmeans_params)

        centroid = kmeans_ret.get('kmeans_ret')
        idx = kmeans_ret.get('idx')

        df = pd.read_json(data_matrix)
        rows = df.index.tolist()

        clusters = {}
        for list_index, value in enumerate(idx):
            cluster = clusters.get(value)
            if not cluster:
                clusters.update({value: {rows[list_index]: list_index}})
            else:
                cluster.update({rows[list_index]: list_index})

        return clusters

    def _build_clustermap(self, data_matrix, metric, method):
        """
        plot cluster heatmap
        https://seaborn.pydata.org/generated/seaborn.clustermap.html
        """
        log('start building seaborn clustermap')
        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(output_directory)
        plot_file = os.path.join(output_directory, 'clustermap.png')

        df = pd.read_json(data_matrix)
        df.fillna(0, inplace=True)

        sns_plot = sns.clustermap(df, method=method, metric=metric)
        sns_plot.savefig(plot_file)

        return plot_file

    def _build_plotly_clustermap(self, data_matrix, dist_metric, linkage_method):

        log('start building plotly page')

        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(output_directory)
        plot_file = os.path.join(output_directory, 'clustermap.html')

        df = pd.read_json(data_matrix)
        df.fillna(0, inplace=True)

        # Initialize figure by creating upper dendrogram
        log('initializing upper dendrogram')
        figure = ff.create_dendrogram(df.T, orientation='bottom', labels=df.T.index,
                                      linkagefun=lambda x: hier.linkage(df.T.values,
                                                                        method=linkage_method,
                                                                        metric=dist_metric))
        for i in range(len(figure['data'])):
            figure['data'][i]['yaxis'] = 'y2'

        # Create Side Dendrogram
        log('creating side dendrogram')
        dendro_side = ff.create_dendrogram(df, orientation='right', labels=df.index,
                                           linkagefun=lambda x: hier.linkage(
                                                                        df.values,
                                                                        method=linkage_method,
                                                                        metric=dist_metric))
        for i in range(len(dendro_side['data'])):
            dendro_side['data'][i]['xaxis'] = 'x2'

        # Add Side Dendrogram Data to Figure
        figure.add_traces(dendro_side['data'])
        # figure['data'].extend(dendro_side['data'])

        # Create Heatmap
        log('creating heatmap')
        heatmap = [go.Heatmap(x=df.columns, y=df.index, z=df.values, colorscale='YlGnBu')]

        original_heatmap_x = heatmap[0]['x']
        original_heatmap_y = heatmap[0]['y']

        heatmap[0]['x'] = figure['layout']['xaxis']['tickvals']
        heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']

        # Add Heatmap Data to Figure
        figure.add_traces(heatmap)
        # figure['data'].extend(heatmap)

        # Edit Layout
        figure['layout'].update({'width': 800, 'height': 800,
                                 'showlegend': False, 'hovermode': 'closest',
                                 })
        # Edit xaxis
        figure['layout']['xaxis'].update({'domain': [.15, 1],
                                          'mirror': False,
                                          'showgrid': False,
                                          'showline': False,
                                          'zeroline': False,
                                          'ticktext': original_heatmap_x,
                                          'ticks': ""})
        # Edit xaxis2
        figure['layout'].update({'xaxis2': {'domain': [0, .15],
                                            'mirror': False,
                                            'showgrid': False,
                                            'showline': False,
                                            'zeroline': False,
                                            'showticklabels': False,
                                            'ticktext': original_heatmap_x,
                                            'ticks': ""}})

        # Edit yaxis
        figure['layout']['yaxis'] = dendro_side['layout']['yaxis']
        figure['layout']['yaxis'].update({'domain': [0, .85],
                                          'mirror': False,
                                          'showgrid': False,
                                          'showline': False,
                                          'zeroline': False,
                                          'showticklabels': False,
                                          'ticktext': original_heatmap_y,
                                          'ticks': ""})
        # Edit yaxis2
        figure['layout'].update({'yaxis2': {'domain': [.825, .975],
                                            'mirror': False,
                                            'showgrid': False,
                                            'showline': False,
                                            'zeroline': False,
                                            'showticklabels': False,
                                            'ticks': ""}})

        log('plotting figure')
        plot(figure, filename=plot_file)

        return plot_file

    def __init__(self, config):
        self.ws_url = config["workspace-url"]
        self.callback_url = config['SDK_CALLBACK_URL']
        self.token = config['KB_AUTH_TOKEN']
        self.shock_url = config['shock-url']
        self.srv_wiz_url = config['srv-wiz-url']
        self.scratch = config['scratch']
        self.dfu = DataFileUtil(self.callback_url)
        self.ke_util = kb_ke_util(self.callback_url, service_ver="dev")
        self.gen_api = GenericsAPI(self.callback_url, service_ver="dev")

        self.ws = Workspace(self.ws_url, token=self.token)
        self.set_client = SetAPI(self.srv_wiz_url)

        plt.switch_backend('agg')

    def run_pca(self, params):
        """
        run_pca: generates PCA matrix for KBaseExperiments.ClusterSet data object

        cluster_set_ref: KBaseExperiments.ClusterSet object references
        workspace_name: the name of the workspace
        pca_matrix_name: name of PCA (KBaseFeatureValues.FloatMatrix2D) object
        n_components - number of components (default 2)

        pca_ref: PCA object reference (as KBaseFeatureValues.FloatMatrix2D data type)
        report_name: report name generated by KBaseReport
        report_ref: report reference generated by KBaseReport
        """

        self._validate_run_pca_params(params)

        cluster_set_ref = params.get('cluster_set_ref')
        workspace_name = params.get('workspace_name')
        pca_matrix_name = params.get('pca_matrix_name')
        n_components = int(params.get('n_components', 2))

        cluster_set_source = self.dfu.get_objects(
                    {"object_refs": [cluster_set_ref]})['data'][0]

        cluster_set_info = cluster_set_source.get('info')
        cluster_set_name = cluster_set_info[1]
        cluster_set_data = cluster_set_source.get('data')
        clusters = cluster_set_data.get('clusters')

        matrix_ref = cluster_set_data.get('original_data')

        data_matrix = self.gen_api.fetch_data({'obj_ref': matrix_ref}).get('data_matrix')

        if '_column' in cluster_set_name:
            data_matrix = pd.read_json(data_matrix).T.to_json()  # transpose matrix

        # run pca algorithm
        pca_params = {'data_matrix': data_matrix,
                      'n_components': n_components}
        PCA_matrix = self.ke_util.run_PCA(pca_params).get('PCA_matrix')

        df = pd.read_json(PCA_matrix)
        df.fillna(0, inplace=True)

        pca_ref,  pca_matrix_data = self._save_2D_matrix(df, clusters,
                                                         workspace_name, pca_matrix_name)

        returnVal = {'pca_ref': pca_ref}

        report_output = self._generate_pca_report(pca_ref, pca_matrix_data, workspace_name)

        returnVal.update(report_output)
        return returnVal

    def run_kmeans_cluster(self, params):
        """
        run_kmeans_cluster: generates Kmeans clusters for Matrix data object

        matrix_ref: Matrix object reference
        workspace_name: the name of the workspace
        cluster_set_name: KBaseExperiments.ClusterSet object name
        k_num: number of clusters to form

        Optional arguments:
        dist_metric: The distance metric to use. Default set to 'euclidean'.
                     The distance function can be
                     ["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine",
                      "dice", "euclidean", "hamming", "jaccard", "kulsinski", "matching",
                      "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath", "sqeuclidean",
                      "yule"]
                     Details refer to:
                     https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html

        return:
        cluster_set_refs: KBaseExperiments.ClusterSet object references
        report_name: report name generated by KBaseReport
        report_ref: report reference generated by KBaseReport
        """

        self._validate_run_kmeans_cluster_params(params)

        matrix_ref = params.get('matrix_ref')
        workspace_name = params.get('workspace_name')
        cluster_set_name = params.get('cluster_set_name')
        k_num = params.get('k_num')
        dist_metric = params.get('dist_metric')

        matrix_object = self.ws.get_objects2({'objects': [{'ref': matrix_ref}]})['data'][0]
        matrix_data = matrix_object['data']

        data_matrix = self.gen_api.fetch_data({'obj_ref': matrix_ref}).get('data_matrix')
        transpose_data_matrix = pd.read_json(data_matrix).T.to_json()

        row_kmeans_clusters = self._build_kmeans_cluster(data_matrix, k_num,
                                                         dist_metric=dist_metric)

        col_kmeans_clusters = self._build_kmeans_cluster(transpose_data_matrix, k_num,
                                                         dist_metric=dist_metric)

        genome_ref = matrix_data.get('genome_ref')
        clustering_parameters = {'k_num': str(k_num),
                                 'dist_metric': str(dist_metric)}

        cluster_set_refs = []

        row_cluster_set_name = cluster_set_name + '_row'
        row_cluster_set = self._build_kmeans_cluster_set(
                                                    row_kmeans_clusters,
                                                    row_cluster_set_name,
                                                    genome_ref,
                                                    matrix_ref,
                                                    matrix_data.get('row_mapping'),
                                                    matrix_data.get('row_conditionset_ref'),
                                                    workspace_name,
                                                    clustering_parameters)
        cluster_set_refs.append(row_cluster_set)

        col_cluster_set_name = cluster_set_name + '_column'
        col_cluster_set = self._build_kmeans_cluster_set(
                                                    col_kmeans_clusters,
                                                    col_cluster_set_name,
                                                    genome_ref,
                                                    matrix_ref,
                                                    matrix_data.get('col_mapping'),
                                                    matrix_data.get('col_conditionset_ref'),
                                                    workspace_name,
                                                    clustering_parameters)
        cluster_set_refs.append(col_cluster_set)

        returnVal = {'cluster_set_refs': cluster_set_refs}

        report_output = self._generate_kmeans_cluster_report(cluster_set_refs, workspace_name)

        returnVal.update(report_output)

        return returnVal

    def run_hierarchical_cluster(self, params):
        """
        run_hierarchical_cluster: generates hierarchical clusters for Matrix data object

        matrix_ref: Matrix object reference
        workspace_name: the name of the workspace
        cluster_set_name: KBaseExperiments.ClusterSet object name
        dist_cutoff_rate: the threshold to apply when forming flat clusters

        Optional arguments:
        dist_metric: The distance metric to use. Default set to 'euclidean'.
                     The distance function can be
                     ["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine",
                      "dice", "euclidean", "hamming", "jaccard", "kulsinski", "matching",
                      "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath",
                      "sqeuclidean", "yule"]
                     Details refer to:
                     https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html

        linkage_method: The linkage algorithm to use. Default set to 'single'.
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
        cluster_set_refs: KBaseExperiments.ClusterSet object references
        report_name: report name generated by KBaseReport
        report_ref: report reference generated by KBaseReport
        """
        log('--->\nrunning run_hierarchical_cluster\n' +
            'params:\n{}'.format(json.dumps(params, indent=1)))

        self._validate_run_hierarchical_cluster_params(params)

        matrix_ref = params.get('matrix_ref')
        workspace_name = params.get('workspace_name')
        cluster_set_name = params.get('cluster_set_name')
        row_dist_cutoff_rate = float(params.get('row_dist_cutoff_rate', 0.5))
        col_dist_cutoff_rate = float(params.get('col_dist_cutoff_rate', 0.5))
        dist_metric = params.get('dist_metric')
        linkage_method = params.get('linkage_method')
        fcluster_criterion = params.get('fcluster_criterion')

        matrix_object = self.ws.get_objects2({'objects': [{'ref':
                                                          matrix_ref}]})['data'][0]
        matrix_data = matrix_object['data']

        data_matrix = self.gen_api.fetch_data({'obj_ref': matrix_ref}).get('data_matrix')
        transpose_data_matrix = pd.read_json(data_matrix).T.to_json()

        # plotly_heatmap = self._build_plotly_clustermap(data_matrix, dist_metric, linkage_method)
        plotly_heatmap = self._build_clustermap(data_matrix, dist_metric, linkage_method)

        (row_flat_cluster,
         row_labels,
         row_newick,
         row_dendrogram_path,
         row_dendrogram_truncate_path) = self._build_flat_cluster(
                                                            data_matrix,
                                                            row_dist_cutoff_rate,
                                                            dist_metric=dist_metric,
                                                            linkage_method=linkage_method,
                                                            fcluster_criterion=fcluster_criterion)

        (col_flat_cluster,
         col_labels,
         col_newick,
         col_dendrogram_path,
         col_dendrogram_truncate_path) = self._build_flat_cluster(
                                                            transpose_data_matrix,
                                                            col_dist_cutoff_rate,
                                                            dist_metric=dist_metric,
                                                            linkage_method=linkage_method,
                                                            fcluster_criterion=fcluster_criterion)

        genome_ref = matrix_data.get('genome_ref')

        clustering_parameters = {'col_dist_cutoff_rate': str(col_dist_cutoff_rate),
                                 'row_dist_cutoff_rate': str(row_dist_cutoff_rate),
                                 'dist_metric': dist_metric,
                                 'linkage_method': linkage_method,
                                 'fcluster_criterion': fcluster_criterion}

        cluster_set_refs = []

        row_cluster_set_name = cluster_set_name + '_row'
        row_cluster_set = self._build_hierarchical_cluster_set(
                                                    row_flat_cluster,
                                                    row_cluster_set_name,
                                                    genome_ref,
                                                    matrix_ref,
                                                    matrix_data.get('row_mapping'),
                                                    matrix_data.get('row_conditionset_ref'),
                                                    workspace_name,
                                                    clustering_parameters,
                                                    data_matrix)
        cluster_set_refs.append(row_cluster_set)

        col_cluster_set_name = cluster_set_name + '_column'
        col_cluster_set = self._build_hierarchical_cluster_set(
                                                    col_flat_cluster,
                                                    col_cluster_set_name,
                                                    genome_ref,
                                                    matrix_ref,
                                                    matrix_data.get('col_mapping'),
                                                    matrix_data.get('col_conditionset_ref'),
                                                    workspace_name,
                                                    clustering_parameters,
                                                    transpose_data_matrix)
        cluster_set_refs.append(col_cluster_set)

        returnVal = {'cluster_set_refs': cluster_set_refs}

        report_output = self._generate_hierarchical_cluster_report(cluster_set_refs,
                                                                   workspace_name,
                                                                   row_dendrogram_path,
                                                                   row_dendrogram_truncate_path,
                                                                   col_dendrogram_path,
                                                                   col_dendrogram_truncate_path,
                                                                   plotly_heatmap)
        returnVal.update(report_output)

        return returnVal
