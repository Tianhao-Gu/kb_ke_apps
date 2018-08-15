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
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from kb_ke_apps.kb_ke_appsImpl import kb_ke_apps
from kb_ke_apps.kb_ke_appsServer import MethodContext
from kb_ke_apps.authclient import KBaseAuth as _KBaseAuth
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil
from DataFileUtil.DataFileUtilClient import DataFileUtil


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

        cls.gfu = GenomeFileUtil(cls.callback_url, service_ver='dev')
        cls.dfu = DataFileUtil(cls.callback_url)

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
        # upload genome object
        genbank_file_name = 'minimal.gbff'
        genbank_file_path = os.path.join(cls.scratch, genbank_file_name)
        shutil.copy(os.path.join('data', genbank_file_name), genbank_file_path)

        genome_object_name = 'test_Genome'
        cls.genome_ref = cls.gfu.genbank_to_genome({'file': {'path': genbank_file_path},
                                                    'workspace_name': cls.wsName,
                                                    'genome_name': genome_object_name,
                                                    'generate_ids_if_needed': 1
                                                    })['genome_ref']

        # upload expression matrix object
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

        # cls.expression_matrix_ref = '5290/238/3'

        # cls.expression_matrix_ref = '5290/258/6'

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
        print('\n*** starting test: ' + testname + ' **')

    def fail_run_expression_matrix_cluster(self, params, error, exception=ValueError, 
                                           contains=False):
        with self.assertRaises(exception) as context:
            self.getImpl().run_expression_matrix_cluster(self.ctx, params)
        if contains:
            self.assertIn(error, str(context.exception.message))
        else:
            self.assertEqual(error, str(context.exception.message))

    def check_run_expression_matrix_cluster_output(self, ret):
        self.assertTrue('feature_set_set_refs' in ret)
        self.assertTrue('report_name' in ret)
        self.assertTrue('report_ref' in ret)

    def test_bad_run_expression_matrix_cluster_params(self):
        self.start_test()
        invalidate_params = {'missing_matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'feature_set_suffix': 'feature_set_suffix',
                             'dist_threshold': 'dist_threshold'}
        error_msg = '"matrix_ref" parameter is required, but missing'
        self.fail_run_expression_matrix_cluster(invalidate_params, error_msg)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'missing_workspace_name': 'workspace_name',
                             'feature_set_suffix': 'feature_set_suffix',
                             'dist_threshold': 'dist_threshold'}
        error_msg = '"workspace_name" parameter is required, but missing'
        self.fail_run_expression_matrix_cluster(invalidate_params, error_msg)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'missing_feature_set_suffix': 'feature_set_suffix',
                             'dist_threshold': 'dist_threshold'}
        error_msg = '"feature_set_suffix" parameter is required, but missing'
        self.fail_run_expression_matrix_cluster(invalidate_params, error_msg)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'feature_set_suffix': 'feature_set_suffix',
                             'missing_dist_threshold': 'dist_threshold'}
        error_msg = '"dist_threshold" parameter is required, but missing'
        self.fail_run_expression_matrix_cluster(invalidate_params, error_msg)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'feature_set_suffix': 'feature_set_suffix',
                             'dist_threshold': 'dist_threshold',
                             'dist_metric': 'invalidate_metric'}
        error_msg = 'INPUT ERROR:\nInput metric function [invalidate_metric] is not valid.\n'
        self.fail_run_expression_matrix_cluster(invalidate_params, error_msg, contains=True)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'feature_set_suffix': 'feature_set_suffix',
                             'dist_threshold': 'dist_threshold',
                             'linkage_method': 'invalidate_method'}
        error_msg = "INPUT ERROR:\nInput linkage algorithm [invalidate_method] is not valid.\n"
        self.fail_run_expression_matrix_cluster(invalidate_params, error_msg, contains=True)

        invalidate_params = {'matrix_ref': 'matrix_ref',
                             'workspace_name': 'workspace_name',
                             'feature_set_suffix': 'feature_set_suffix',
                             'dist_threshold': 'dist_threshold',
                             'fcluster_criterion': 'invalidate_criterion'}
        error_msg = "INPUT ERROR:\nInput criterion [invalidate_criterion] is not valid.\n"
        self.fail_run_expression_matrix_cluster(invalidate_params, error_msg, contains=True)

    def test_run_expression_matrix_cluster(self):
        self.start_test()

        params = {'matrix_ref': self.expression_matrix_ref,
                  'workspace_name': self.getWsName(),
                  'feature_set_suffix': '_cluster',
                  'dist_threshold': 100,
                  'dist_metric': 'cityblock',
                  'linkage_method': 'ward',
                  'fcluster_criterion': 'distance'}
        ret = self.getImpl().run_expression_matrix_cluster(self.ctx, params)[0]
        self.check_run_expression_matrix_cluster_output(ret)
