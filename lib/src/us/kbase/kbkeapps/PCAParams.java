
package us.kbase.kbkeapps;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: PCAParams</p>
 * <pre>
 * Input of the run_pca function
 * cluster_set_ref: KBaseExperiments.ClusterSet object references
 * workspace_name: the name of the workspace
 * pca_matrix_suffix: suffix append to PCA (KBaseFeatureValues.FloatMatrix2D) object name
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "cluster_set_ref",
    "workspace_name",
    "pca_matrix_suffix"
})
public class PCAParams {

    @JsonProperty("cluster_set_ref")
    private String clusterSetRef;
    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("pca_matrix_suffix")
    private String pcaMatrixSuffix;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("cluster_set_ref")
    public String getClusterSetRef() {
        return clusterSetRef;
    }

    @JsonProperty("cluster_set_ref")
    public void setClusterSetRef(String clusterSetRef) {
        this.clusterSetRef = clusterSetRef;
    }

    public PCAParams withClusterSetRef(String clusterSetRef) {
        this.clusterSetRef = clusterSetRef;
        return this;
    }

    @JsonProperty("workspace_name")
    public String getWorkspaceName() {
        return workspaceName;
    }

    @JsonProperty("workspace_name")
    public void setWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
    }

    public PCAParams withWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
        return this;
    }

    @JsonProperty("pca_matrix_suffix")
    public String getPcaMatrixSuffix() {
        return pcaMatrixSuffix;
    }

    @JsonProperty("pca_matrix_suffix")
    public void setPcaMatrixSuffix(String pcaMatrixSuffix) {
        this.pcaMatrixSuffix = pcaMatrixSuffix;
    }

    public PCAParams withPcaMatrixSuffix(String pcaMatrixSuffix) {
        this.pcaMatrixSuffix = pcaMatrixSuffix;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((("PCAParams"+" [clusterSetRef=")+ clusterSetRef)+", workspaceName=")+ workspaceName)+", pcaMatrixSuffix=")+ pcaMatrixSuffix)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
