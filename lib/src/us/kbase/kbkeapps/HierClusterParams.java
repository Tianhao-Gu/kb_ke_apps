
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
 * <p>Original spec-file type: HierClusterParams</p>
 * <pre>
 * Input of the run_hierarchical_cluster function
 * matrix_ref: Matrix object reference
 * workspace_name: the name of the workspace
 * cluster_set_name: KBaseExperiments.ClusterSet object name
 * dist_cutoff_rate: the threshold to apply when forming flat clusters
 * Optional arguments:
 * dist_metric: The distance metric to use. Default set to 'euclidean'.
 *              The distance function can be
 *              ["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine", 
 *               "dice", "euclidean", "hamming", "jaccard", "kulsinski", "matching", 
 *               "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath", "sqeuclidean", 
 *               "yule"]
 *              Details refer to:
 *              https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html
 * linkage_method: The linkage algorithm to use. Default set to 'ward'.
 *                 The method can be
 *                 ["single", "complete", "average", "weighted", "centroid", "median", "ward"]
 *                 Details refer to:
 *                 https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html
 * fcluster_criterion: The criterion to use in forming flat clusters. Default set to 'distance'.
 *                     The criterion can be
 *                     ["inconsistent", "distance", "maxclust"]
 *                     Details refer to:
 *                     https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.fcluster.html
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "matrix_ref",
    "workspace_name",
    "cluster_set_name",
    "row_dist_cutoff_rate",
    "col_dist_cutoff_rate",
    "dist_metric",
    "linkage_method",
    "fcluster_criterion"
})
public class HierClusterParams {

    @JsonProperty("matrix_ref")
    private String matrixRef;
    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("cluster_set_name")
    private String clusterSetName;
    @JsonProperty("row_dist_cutoff_rate")
    private Double rowDistCutoffRate;
    @JsonProperty("col_dist_cutoff_rate")
    private Double colDistCutoffRate;
    @JsonProperty("dist_metric")
    private String distMetric;
    @JsonProperty("linkage_method")
    private String linkageMethod;
    @JsonProperty("fcluster_criterion")
    private String fclusterCriterion;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("matrix_ref")
    public String getMatrixRef() {
        return matrixRef;
    }

    @JsonProperty("matrix_ref")
    public void setMatrixRef(String matrixRef) {
        this.matrixRef = matrixRef;
    }

    public HierClusterParams withMatrixRef(String matrixRef) {
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

    public HierClusterParams withWorkspaceName(String workspaceName) {
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

    public HierClusterParams withClusterSetName(String clusterSetName) {
        this.clusterSetName = clusterSetName;
        return this;
    }

    @JsonProperty("row_dist_cutoff_rate")
    public Double getRowDistCutoffRate() {
        return rowDistCutoffRate;
    }

    @JsonProperty("row_dist_cutoff_rate")
    public void setRowDistCutoffRate(Double rowDistCutoffRate) {
        this.rowDistCutoffRate = rowDistCutoffRate;
    }

    public HierClusterParams withRowDistCutoffRate(Double rowDistCutoffRate) {
        this.rowDistCutoffRate = rowDistCutoffRate;
        return this;
    }

    @JsonProperty("col_dist_cutoff_rate")
    public Double getColDistCutoffRate() {
        return colDistCutoffRate;
    }

    @JsonProperty("col_dist_cutoff_rate")
    public void setColDistCutoffRate(Double colDistCutoffRate) {
        this.colDistCutoffRate = colDistCutoffRate;
    }

    public HierClusterParams withColDistCutoffRate(Double colDistCutoffRate) {
        this.colDistCutoffRate = colDistCutoffRate;
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

    public HierClusterParams withDistMetric(String distMetric) {
        this.distMetric = distMetric;
        return this;
    }

    @JsonProperty("linkage_method")
    public String getLinkageMethod() {
        return linkageMethod;
    }

    @JsonProperty("linkage_method")
    public void setLinkageMethod(String linkageMethod) {
        this.linkageMethod = linkageMethod;
    }

    public HierClusterParams withLinkageMethod(String linkageMethod) {
        this.linkageMethod = linkageMethod;
        return this;
    }

    @JsonProperty("fcluster_criterion")
    public String getFclusterCriterion() {
        return fclusterCriterion;
    }

    @JsonProperty("fcluster_criterion")
    public void setFclusterCriterion(String fclusterCriterion) {
        this.fclusterCriterion = fclusterCriterion;
    }

    public HierClusterParams withFclusterCriterion(String fclusterCriterion) {
        this.fclusterCriterion = fclusterCriterion;
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
        return ((((((((((((((((((("HierClusterParams"+" [matrixRef=")+ matrixRef)+", workspaceName=")+ workspaceName)+", clusterSetName=")+ clusterSetName)+", rowDistCutoffRate=")+ rowDistCutoffRate)+", colDistCutoffRate=")+ colDistCutoffRate)+", distMetric=")+ distMetric)+", linkageMethod=")+ linkageMethod)+", fclusterCriterion=")+ fclusterCriterion)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
