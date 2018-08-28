
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
 * <p>Original spec-file type: KmeansClusterParams</p>
 * <pre>
 * Input of the run_kmeans_cluster function
 * matrix_ref: Matrix object reference
 * workspace_name: the name of the workspace
 * cluster_set_name: KBaseExperiments.ClusterSet object name
 * k_num: number of clusters to form
 * Optional arguments:
 * dist_metric: The distance metric to use. Default set to 'euclidean'.
 *              The distance function can be
 *              ["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine", 
 *               "dice", "euclidean", "hamming", "jaccard", "kulsinski", "matching", 
 *               "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath", "sqeuclidean", 
 *               "yule"]
 *              Details refer to:
 *              https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "matrix_ref",
    "workspace_name",
    "cluster_set_name",
    "k_num",
    "dist_metric"
})
public class KmeansClusterParams {

    @JsonProperty("matrix_ref")
    private String matrixRef;
    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("cluster_set_name")
    private String clusterSetName;
    @JsonProperty("k_num")
    private Long kNum;
    @JsonProperty("dist_metric")
    private String distMetric;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("matrix_ref")
    public String getMatrixRef() {
        return matrixRef;
    }

    @JsonProperty("matrix_ref")
    public void setMatrixRef(String matrixRef) {
        this.matrixRef = matrixRef;
    }

    public KmeansClusterParams withMatrixRef(String matrixRef) {
        this.matrixRef = matrixRef;
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

    public KmeansClusterParams withWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
        return this;
    }

    @JsonProperty("cluster_set_name")
    public String getClusterSetName() {
        return clusterSetName;
    }

    @JsonProperty("cluster_set_name")
    public void setClusterSetName(String clusterSetName) {
        this.clusterSetName = clusterSetName;
    }

    public KmeansClusterParams withClusterSetName(String clusterSetName) {
        this.clusterSetName = clusterSetName;
        return this;
    }

    @JsonProperty("k_num")
    public Long getKNum() {
        return kNum;
    }

    @JsonProperty("k_num")
    public void setKNum(Long kNum) {
        this.kNum = kNum;
    }

    public KmeansClusterParams withKNum(Long kNum) {
        this.kNum = kNum;
        return this;
    }

    @JsonProperty("dist_metric")
    public String getDistMetric() {
        return distMetric;
    }

    @JsonProperty("dist_metric")
    public void setDistMetric(String distMetric) {
        this.distMetric = distMetric;
    }

    public KmeansClusterParams withDistMetric(String distMetric) {
        this.distMetric = distMetric;
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
        return ((((((((((((("KmeansClusterParams"+" [matrixRef=")+ matrixRef)+", workspaceName=")+ workspaceName)+", clusterSetName=")+ clusterSetName)+", kNum=")+ kNum)+", distMetric=")+ distMetric)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
