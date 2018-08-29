
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
 * pca_matrix_name: name of PCA (KBaseFeatureValues.FloatMatrix2D) object
 * n_components - number of components (default 2)
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "cluster_set_ref",
    "workspace_name",
    "pca_matrix_name",
    "n_components"
})
public class PCAParams {

    @JsonProperty("cluster_set_ref")
    private String clusterSetRef;
    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("pca_matrix_name")
    private String pcaMatrixName;
    @JsonProperty("n_components")
    private Long nComponents;
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

    @JsonProperty("pca_matrix_name")
    public String getPcaMatrixName() {
        return pcaMatrixName;
    }

    @JsonProperty("pca_matrix_name")
    public void setPcaMatrixName(String pcaMatrixName) {
        this.pcaMatrixName = pcaMatrixName;
    }

    public PCAParams withPcaMatrixName(String pcaMatrixName) {
        this.pcaMatrixName = pcaMatrixName;
        return this;
    }

    @JsonProperty("n_components")
    public Long getNComponents() {
        return nComponents;
    }

    @JsonProperty("n_components")
    public void setNComponents(Long nComponents) {
        this.nComponents = nComponents;
    }

    public PCAParams withNComponents(Long nComponents) {
        this.nComponents = nComponents;
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
        return ((((((((((("PCAParams"+" [clusterSetRef=")+ clusterSetRef)+", workspaceName=")+ workspaceName)+", pcaMatrixName=")+ pcaMatrixName)+", nComponents=")+ nComponents)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
