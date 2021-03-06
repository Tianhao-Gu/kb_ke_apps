
package us.kbase.kbkeapps;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: KmeansClusterOutput</p>
 * <pre>
 * Ouput of the run_kmeans_cluster function
 * cluster_set_refs: KBaseExperiments.ClusterSet object references
 * report_name: report name generated by KBaseReport
 * report_ref: report reference generated by KBaseReport
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "cluster_set_refs",
    "report_name",
    "report_ref"
})
public class KmeansClusterOutput {

    @JsonProperty("cluster_set_refs")
    private List<String> clusterSetRefs;
    @JsonProperty("report_name")
    private java.lang.String reportName;
    @JsonProperty("report_ref")
    private java.lang.String reportRef;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("cluster_set_refs")
    public List<String> getClusterSetRefs() {
        return clusterSetRefs;
    }

    @JsonProperty("cluster_set_refs")
    public void setClusterSetRefs(List<String> clusterSetRefs) {
        this.clusterSetRefs = clusterSetRefs;
    }

    public KmeansClusterOutput withClusterSetRefs(List<String> clusterSetRefs) {
        this.clusterSetRefs = clusterSetRefs;
        return this;
    }

    @JsonProperty("report_name")
    public java.lang.String getReportName() {
        return reportName;
    }

    @JsonProperty("report_name")
    public void setReportName(java.lang.String reportName) {
        this.reportName = reportName;
    }

    public KmeansClusterOutput withReportName(java.lang.String reportName) {
        this.reportName = reportName;
        return this;
    }

    @JsonProperty("report_ref")
    public java.lang.String getReportRef() {
        return reportRef;
    }

    @JsonProperty("report_ref")
    public void setReportRef(java.lang.String reportRef) {
        this.reportRef = reportRef;
    }

    public KmeansClusterOutput withReportRef(java.lang.String reportRef) {
        this.reportRef = reportRef;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((("KmeansClusterOutput"+" [clusterSetRefs=")+ clusterSetRefs)+", reportName=")+ reportName)+", reportRef=")+ reportRef)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
