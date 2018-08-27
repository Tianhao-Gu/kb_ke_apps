# -*- coding: utf-8 -*-
############################################################
#
# Autogenerated by the KBase type compiler -
# any changes made here will be overwritten
#
############################################################

from __future__ import print_function
# the following is a hack to get the baseclient to import whether we're in a
# package or not. This makes pep8 unhappy hence the annotations.
try:
    # baseclient and this client are in a package
    from .baseclient import BaseClient as _BaseClient  # @UnusedImport
except:
    # no they aren't
    from baseclient import BaseClient as _BaseClient  # @Reimport
import time


class GenericsAPI(object):

    def __init__(
            self, url=None, timeout=30 * 60, user_id=None,
            password=None, token=None, ignore_authrc=False,
            trust_all_ssl_certificates=False,
            auth_svc='https://kbase.us/services/authorization/Sessions/Login',
            service_ver='release',
            async_job_check_time_ms=100, async_job_check_time_scale_percent=150, 
            async_job_check_max_time_ms=300000):
        if url is None:
            raise ValueError('A url is required')
        self._service_ver = service_ver
        self._client = _BaseClient(
            url, timeout=timeout, user_id=user_id, password=password,
            token=token, ignore_authrc=ignore_authrc,
            trust_all_ssl_certificates=trust_all_ssl_certificates,
            auth_svc=auth_svc,
            async_job_check_time_ms=async_job_check_time_ms,
            async_job_check_time_scale_percent=async_job_check_time_scale_percent,
            async_job_check_max_time_ms=async_job_check_max_time_ms)

    def _check_job(self, job_id):
        return self._client._check_job('GenericsAPI', job_id)

    def _fetch_data_submit(self, params, context=None):
        return self._client._submit_job(
             'GenericsAPI.fetch_data', [params],
             self._service_ver, context)

    def fetch_data(self, params, context=None):
        """
        fetch_data: fetch generics data as pandas dataframe for a generics data object
        :param params: instance of type "FetchDataParams" (Input of the
           fetch_data function obj_ref: generics object reference Optional
           arguments: generics_module: the generics data module to be
           retrieved from e.g. for an given data type like below: typedef
           structure { FloatMatrix2D data; condition_set_ref
           condition_set_ref; } SomeGenericsMatrix; generics_module should be
           {'data': 'FloatMatrix2D', 'condition_set_ref':
           'condition_set_ref'}) -> structure: parameter "obj_ref" of type
           "obj_ref" (An X/Y/Z style reference), parameter "generics_module"
           of mapping from String to String
        :returns: instance of type "FetchDataReturn" (Ouput of the fetch_data
           function data_matrix: a pandas dataframe in json format) ->
           structure: parameter "data_matrix" of String
        """
        job_id = self._fetch_data_submit(params, context)
        async_job_check_time = self._client.async_job_check_time
        while True:
            time.sleep(async_job_check_time)
            async_job_check_time = (async_job_check_time *
                self._client.async_job_check_time_scale_percent / 100.0)
            if async_job_check_time > self._client.async_job_check_max_time:
                async_job_check_time = self._client.async_job_check_max_time
            job_state = self._check_job(job_id)
            if job_state['finished']:
                return job_state['result'][0]

    def _generate_matrix_html_submit(self, params, context=None):
        return self._client._submit_job(
             'GenericsAPI.generate_matrix_html', [params],
             self._service_ver, context)

    def generate_matrix_html(self, params, context=None):
        """
        generate_matrix_html: generate a html page for given data
        :param params: instance of type "GenMatrixHTMLParams" (Input of the
           generate_matrix_html function df: a pandas dataframe) ->
           structure: parameter "df" of mapping from String to String
        :returns: instance of type "GenMatrixHTMLReturn" (Ouput of the
           generate_matrix_html function html_string: html as a string
           format) -> structure: parameter "html_string" of String
        """
        job_id = self._generate_matrix_html_submit(params, context)
        async_job_check_time = self._client.async_job_check_time
        while True:
            time.sleep(async_job_check_time)
            async_job_check_time = (async_job_check_time *
                self._client.async_job_check_time_scale_percent / 100.0)
            if async_job_check_time > self._client.async_job_check_max_time:
                async_job_check_time = self._client.async_job_check_max_time
            job_state = self._check_job(job_id)
            if job_state['finished']:
                return job_state['result'][0]

    def _export_matrix_submit(self, params, context=None):
        return self._client._submit_job(
             'GenericsAPI.export_matrix', [params],
             self._service_ver, context)

    def export_matrix(self, params, context=None):
        """
        :param params: instance of type "ExportParams" (Input of the
           export_matrix function obj_ref: generics object reference Optional
           arguments: generics_module: select the generics data to be
           retrieved from e.g. for an given data type like below: typedef
           structure { FloatMatrix2D data; condition_set_ref
           condition_set_ref; } SomeGenericsMatrix; and only 'FloatMatrix2D'
           is needed generics_module should be {'data': FloatMatrix2D'}) ->
           structure: parameter "obj_ref" of type "obj_ref" (An X/Y/Z style
           reference), parameter "generics_module" of mapping from String to
           String
        :returns: instance of type "ExportOutput" -> structure: parameter
           "shock_id" of String
        """
        job_id = self._export_matrix_submit(params, context)
        async_job_check_time = self._client.async_job_check_time
        while True:
            time.sleep(async_job_check_time)
            async_job_check_time = (async_job_check_time *
                self._client.async_job_check_time_scale_percent / 100.0)
            if async_job_check_time > self._client.async_job_check_max_time:
                async_job_check_time = self._client.async_job_check_max_time
            job_state = self._check_job(job_id)
            if job_state['finished']:
                return job_state['result'][0]

    def _validate_data_submit(self, params, context=None):
        return self._client._submit_job(
             'GenericsAPI.validate_data', [params],
             self._service_ver, context)

    def validate_data(self, params, context=None):
        """
        validate_data: validate data
        :param params: instance of type "ValidateParams" (Input of the
           validate_data function obj_type: obj type e.g.:
           'KBaseMatrices.ExpressionMatrix-1.1' data: data to be validated)
           -> structure: parameter "obj_type" of String, parameter "data" of
           mapping from String to String
        :returns: instance of type "ValidateOutput" -> structure: parameter
           "validated" of type "boolean" (A boolean - 0 for false, 1 for
           true. @range (0, 1)), parameter "failed_constraint" of mapping
           from String to String
        """
        job_id = self._validate_data_submit(params, context)
        async_job_check_time = self._client.async_job_check_time
        while True:
            time.sleep(async_job_check_time)
            async_job_check_time = (async_job_check_time *
                self._client.async_job_check_time_scale_percent / 100.0)
            if async_job_check_time > self._client.async_job_check_max_time:
                async_job_check_time = self._client.async_job_check_max_time
            job_state = self._check_job(job_id)
            if job_state['finished']:
                return job_state['result'][0]

    def _import_matrix_from_excel_submit(self, params, context=None):
        return self._client._submit_job(
             'GenericsAPI.import_matrix_from_excel', [params],
             self._service_ver, context)

    def import_matrix_from_excel(self, params, context=None):
        """
        import_matrix_from_excel: import matrix object from excel
        :param params: instance of type "ImportMatrixParams" (Input of the
           import_matrix_from_excel function obj_type: one of
           ExpressionMatrix, FitnessMatrix, DifferentialExpressionMatrix
           input_shock_id: file shock id input_file_path: absolute file path
           input_staging_file_path: staging area file path matrix_name:
           matrix object name workspace_name: workspace name matrix object to
           be saved to optional: col_conditionset_ref: column ConditionSet
           reference row_conditionset_ref: row ConditionSet reference
           genome_ref: genome reference diff_expr_matrix_ref:
           DifferentialExpressionMatrix reference) -> structure: parameter
           "obj_type" of String, parameter "input_shock_id" of String,
           parameter "input_file_path" of String, parameter
           "input_staging_file_path" of String, parameter "matrix_name" of
           String, parameter "workspace_name" of type "workspace_name"
           (workspace name of the object), parameter "genome_ref" of type
           "obj_ref" (An X/Y/Z style reference), parameter
           "col_conditionset_ref" of type "obj_ref" (An X/Y/Z style
           reference), parameter "row_conditionset_ref" of type "obj_ref" (An
           X/Y/Z style reference), parameter "diff_expr_matrix_ref" of type
           "obj_ref" (An X/Y/Z style reference)
        :returns: instance of type "ImportMatrixOutput" -> structure:
           parameter "report_name" of String, parameter "report_ref" of
           String, parameter "matrix_obj_ref" of type "obj_ref" (An X/Y/Z
           style reference)
        """
        job_id = self._import_matrix_from_excel_submit(params, context)
        async_job_check_time = self._client.async_job_check_time
        while True:
            time.sleep(async_job_check_time)
            async_job_check_time = (async_job_check_time *
                self._client.async_job_check_time_scale_percent / 100.0)
            if async_job_check_time > self._client.async_job_check_max_time:
                async_job_check_time = self._client.async_job_check_max_time
            job_state = self._check_job(job_id)
            if job_state['finished']:
                return job_state['result'][0]

    def _save_object_submit(self, params, context=None):
        return self._client._submit_job(
             'GenericsAPI.save_object', [params],
             self._service_ver, context)

    def save_object(self, params, context=None):
        """
        save_object: validate data constraints and save matrix object
        :param params: instance of type "SaveObjectParams" (Input of the
           import_matrix_from_excel function obj_type: saving object data
           type obj_name: saving object name data: data to be saved
           workspace_name: workspace name matrix object to be saved to) ->
           structure: parameter "obj_type" of String, parameter "obj_name" of
           String, parameter "data" of mapping from String to String,
           parameter "workspace_name" of type "workspace_name" (workspace
           name of the object)
        :returns: instance of type "SaveObjectOutput" -> structure: parameter
           "obj_ref" of type "obj_ref" (An X/Y/Z style reference)
        """
        job_id = self._save_object_submit(params, context)
        async_job_check_time = self._client.async_job_check_time
        while True:
            time.sleep(async_job_check_time)
            async_job_check_time = (async_job_check_time *
                self._client.async_job_check_time_scale_percent / 100.0)
            if async_job_check_time > self._client.async_job_check_max_time:
                async_job_check_time = self._client.async_job_check_max_time
            job_state = self._check_job(job_id)
            if job_state['finished']:
                return job_state['result'][0]

    def status(self, context=None):
        job_id = self._client._submit_job('GenericsAPI.status', 
            [], self._service_ver, context)
        async_job_check_time = self._client.async_job_check_time
        while True:
            time.sleep(async_job_check_time)
            async_job_check_time = (async_job_check_time *
                self._client.async_job_check_time_scale_percent / 100.0)
            if async_job_check_time > self._client.async_job_check_max_time:
                async_job_check_time = self._client.async_job_check_max_time
            job_state = self._check_job(job_id)
            if job_state['finished']:
                return job_state['result'][0]