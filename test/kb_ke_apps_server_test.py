# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests  # noqa: F401
import inspect
import shutil

from os import environ
try:
    from configparser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from kb_ke_apps.kb_ke_appsImpl import kb_ke_apps
from kb_ke_apps.kb_ke_appsServer import MethodContext
from kb_ke_apps.authclient import KBaseAuth as _KBaseAuth
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil
from DataFileUtil.DataFileUtilClient import DataFileUtil
from GenericsAPI.GenericsAPIClient import GenericsAPI


class kb_ke_appsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_ke_apps'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_ke_apps',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = kb_ke_apps(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

        cls.gfu = GenomeFileUtil(cls.callback_url)
        cls.dfu = DataFileUtil(cls.callback_url)
        cls.gen_api = GenericsAPI(cls.callback_url, service_ver='dev')

        suffix = int(time.time() * 1000)
        cls.wsName = "test_kb_ke_apps_" + str(suffix)
        cls.wsClient.create_workspace({'workspace': cls.wsName})

        cls.prepare_data()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    @classmethod
    def prepare_data(cls):
        # upload Genome object
        genbank_file_name = 'minimal.gbff'
        genbank_file_path = os.path.join(cls.scratch, genbank_file_name)
        shutil.copy(os.path.join('data', genbank_file_name), genbank_file_path)

        genome_object_name = 'test_Genome'
        cls.genome_ref = cls.gfu.genbank_to_genome({'file': {'path': genbank_file_path},
                                                    'workspace_name': cls.wsName,
                                                    'genome_name': genome_object_name,
                                                    'generate_ids_if_needed': 1
                                                    })['genome_ref']

        # upload KBaseFeatureValues.ExpressionMatrix object
        workspace_id = cls.dfu.ws_name_to_id(cls.wsName)
        object_type = 'KBaseFeatureValues.ExpressionMatrix'
        expression_matrix_object_name = 'test_expression_matrix'
        expression_matrix_data = {'genome_ref': cls.genome_ref,
                                  'scale': 'log2',
                                  'type': 'level',
                                  'data': {'row_ids': ['gene_1', 'gene_2', 'gene_3'],
                                           'col_ids': ['condition_1', 'condition_2',
                                                       'condition_3', 'condition_4'],
                                           'values': [[0.1, 0.2, 0.3, 0.4],
                                                      [0.3, 0.4, 0.5, 0.6],
                                                      [None, None, None, None]]
                                           },
                                  'feature_mapping': {},
                                  'condition_mapping': {}}
        save_object_params = {
            'id': workspace_id,
            'objects': [{'type': object_type,
                         'data': expression_matrix_data,
                         'name': expression_matrix_object_name}]
        }

        dfu_oi = cls.dfu.save_objects(save_object_params)[0]
        cls.expression_matrix_ref = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])

        # upload KBaseMatrices.ExpressionMatrix object
        matrix_file_name = 'test_import.xlsx'
        matrix_file_path = os.path.join(cls.scratch, matrix_file_name)
        shutil.copy(os.path.join('data', matrix_file_name), matrix_file_path)

        obj_type = 'ExpressionMatrix'
        params = {'obj_type': obj_type,
                  'matrix_name': 'test_ExpressionMatrix',
                  'workspace_name': cls.wsName,
                  'input_file_path': matrix_file_path,
                  'genome_ref': cls.genome_ref,
                  'scale': 'raw'}
        gen_api_ret = cls.gen_api.import_matrix_from_excel(params)

        cls.matrix_obj_ref = gen_api_ret.get('matrix_obj_ref')
        matrix_obj_data = cls.dfu.get_objects(
            {"object_refs": [cls.matrix_obj_ref]})['data'][0]['data']

        cls.col_conditionset_ref = matrix_obj_data.get('col_attributemapping_ref')
        cls.row_conditionset_ref = matrix_obj_data.get('row_attributemapping_ref')

        # upload KBaseExperiments.ClusterSet object
        object_type = 'KBaseExperiments.ClusterSet'
        cluster_set_object_name = 'test_clusterset'
        cluster_set_data = {'clustering_parameters': {'dist_metric': 'cityblock',
                                                      'k_num': '2'},
                            'clusters': [{'id_to_condition': {
                                            'WRI_RS00015_CDS_1': 'test_row_condition_2',
                                            'WRI_RS00025_CDS_1': 'test_row_condition_3'},
                                          'id_to_data_position': {
                                            'WRI_RS00015_CDS_1': 1,
                                            'WRI_RS00025_CDS_1': 2}},
                                         {'id_to_condition': {
                                            'WRI_RS00010_CDS_1': 'test_row_condition_1'},
                                         'id_to_data_position': {
                                            'WRI_RS00010_CDS_1': 0}}],
                            'condition_set_ref': cls.row_conditionset_ref,
                            'genome_ref': cls.genome_ref,
                            'original_data': cls.matrix_obj_ref}

        save_object_params = {
            'id': workspace_id,
            'objects': [{'type': object_type,
                         'data': cluster_set_data,
                         'name': cluster_set_object_name}]
        }

        dfu_oi = cls.dfu.save_objects(save_object_params)[0]
        cls.cluster_set_ref = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        return self.__class__.wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def start_test(self):
        testname = inspect.stack()[1][3]
        print(('\n*** starting test: ' + testname + ' **'))

    def fail_run_hierarchical_cluster(self, params, error, exception=ValueError,
                                      contains=False):
        with self.assertRaises(exception) as context:
            self.getImpl().run_hierarchical_cluster(self.ctx, params)
        if contains:
            self.assertIn(error, str(context.exception.args[0]))
        else:
            self.assertEqual(error, str(context.exception.args[0]))

    def fail_run_kmeans_cluster(self, params, error, exception=ValueError,
                                contains=False):
        with self.assertRaises(exception) as context:
            self.getImpl().run_kmeans_cluster(self.ctx, params)
        if contains:
            self.assertIn(error, str(context.exception.args[0]))
        else:
            self.assertEqual(error, str(context.exception.args[0]))

    def fail_run_pca(self, params, error, exception=ValueError,
                     contains=False):
        with self.assertRaises(exception) as context:
            self.getImpl().run_pca(self.ctx, params)
        if contains:
            self.assertIn(error, str(context.exception.args[0]))
        else:
            self.assertEqual(error, str(context.exception.args[0]))

    def check_run_hierarchical_cluster_output(self, ret):
        self.assertTrue('cluster_set_refs' in ret)
        self.assertTrue('report_name' in ret)
        self.assertTrue('report_ref' in ret)

    def check_run_kmeans_cluster_output(self, ret):
        self.assertTrue('cluster_set_refs' in ret)
        self.assertTrue('report_name' in ret)
        self.assertTrue('report_ref' in ret)

    def test_bad_run_hierarchical_cluster_params(self):
        self.start_test()
        invalidate_params = {'missing_matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'cluster_set_name': 'cluster_set_name'}
        error_msg = '"matrix_ref" parameter is required, but missing'
        self.fail_run_hierarchical_cluster(invalidate_params, error_msg)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'missing_workspace_name': 'workspace_name',
                             'cluster_set_name': 'cluster_set_name'}
        error_msg = '"workspace_name" parameter is required, but missing'
        self.fail_run_hierarchical_cluster(invalidate_params, error_msg)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'missing_cluster_set_name': 'cluster_set_name'}
        error_msg = '"cluster_set_name" parameter is required, but missing'
        self.fail_run_hierarchical_cluster(invalidate_params, error_msg)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'cluster_set_name': 'cluster_set_name',
                             'dist_cutoff_rate': 'dist_cutoff_rate',
                             'dist_metric': 'invalidate_metric'}
        error_msg = 'INPUT ERROR:\nInput metric function [invalidate_metric] is not valid.\n'
        self.fail_run_hierarchical_cluster(invalidate_params, error_msg, contains=True)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'cluster_set_name': 'cluster_set_name',
                             'dist_cutoff_rate': 'dist_cutoff_rate',
                             'linkage_method': 'invalidate_method'}
        error_msg = "INPUT ERROR:\nInput linkage algorithm [invalidate_method] is not valid.\n"
        self.fail_run_hierarchical_cluster(invalidate_params, error_msg, contains=True)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'cluster_set_name': 'cluster_set_name',
                             'dist_cutoff_rate': 'dist_cutoff_rate',
                             'fcluster_criterion': 'invalidate_criterion'}
        error_msg = "INPUT ERROR:\nInput criterion [invalidate_criterion] is not valid.\n"
        self.fail_run_hierarchical_cluster(invalidate_params, error_msg, contains=True)

    def test_bad_run_kmeans_cluster_params(self):
        self.start_test()
        invalidate_params = {'missing_matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'cluster_set_name': 'cluster_set_name',
                             'k_num': 'k_num'}
        error_msg = '"matrix_ref" parameter is required, but missing'
        self.fail_run_kmeans_cluster(invalidate_params, error_msg)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'cluster_set_name': 'cluster_set_name',
                             'k_num': 'k_num',
                             'dist_metric': 'invalidate_metric'}
        error_msg = 'INPUT ERROR:\nInput metric function [invalidate_metric] is not valid.\n'
        self.fail_run_kmeans_cluster(invalidate_params, error_msg, contains=True)

    def test_run_hierarchical_cluster(self):
        self.start_test()

        params = {'matrix_ref': self.expression_matrix_ref,
                  'workspace_name': self.getWsName(),
                  'cluster_set_name': 'test_hierarchical_cluster_1',
                  'dist_metric': 'euclidean',
                  'linkage_method': 'ward',
                  'fcluster_criterion': 'distance'}
        ret = self.getImpl().run_hierarchical_cluster(self.ctx, params)[0]
        self.check_run_hierarchical_cluster_output(ret)

        params = {'matrix_ref': self.matrix_obj_ref,
                  'workspace_name': self.getWsName(),
                  'cluster_set_name': 'test_hierarchical_cluster_2',
                  'col_dist_cutoff_rate': 0.6,
                  'row_dist_cutoff_rate': 0.6,
                  'dist_metric': 'euclidean',
                  'linkage_method': 'single',
                  'fcluster_criterion': 'distance'}
        ret = self.getImpl().run_hierarchical_cluster(self.ctx, params)[0]
        self.check_run_hierarchical_cluster_output(ret)

    def test_run_kmeans_cluster(self):
        self.start_test()

        params = {'matrix_ref': self.matrix_obj_ref,
                  'workspace_name': self.getWsName(),
                  'cluster_set_name': 'test_kmeans_cluster',
                  'k_num': 2,
                  'dist_metric': 'cityblock'}
        ret = self.getImpl().run_kmeans_cluster(self.ctx, params)[0]
        self.check_run_kmeans_cluster_output(ret)
