package kb_ke_apps::kb_ke_appsClient;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

kb_ke_apps::kb_ke_appsClient

=head1 DESCRIPTION


A KBase module: kb_ke_apps


=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => kb_ke_apps::kb_ke_appsClient::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my %arg_hash2 = @args;
	if (exists $arg_hash2{"token"}) {
	    $self->{token} = $arg_hash2{"token"};
	} elsif (exists $arg_hash2{"user_id"}) {
	    my $token = Bio::KBase::AuthToken->new(@args);
	    if (!$token->error_message) {
	        $self->{token} = $token->token;
	    }
	}
	
	if (exists $self->{token})
	{
	    $self->{client}->{token} = $self->{token};
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 run_expression_matrix_cluster

  $returnVal = $obj->run_expression_matrix_cluster($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ke_apps.EMClusterParams
$returnVal is a kb_ke_apps.EMClusterOutput
EMClusterParams is a reference to a hash where the following keys are defined:
	matrix_ref has a value which is a kb_ke_apps.obj_ref
	workspace_name has a value which is a string
	feature_set_suffix has a value which is a string
	dist_threshold has a value which is a float
	dist_metric has a value which is a string
	linkage_method has a value which is a string
	fcluster_criterion has a value which is a string
obj_ref is a string
EMClusterOutput is a reference to a hash where the following keys are defined:
	feature_set_set_refs has a value which is a reference to a list where each element is a kb_ke_apps.obj_ref
	report_name has a value which is a string
	report_ref has a value which is a string

</pre>

=end html

=begin text

$params is a kb_ke_apps.EMClusterParams
$returnVal is a kb_ke_apps.EMClusterOutput
EMClusterParams is a reference to a hash where the following keys are defined:
	matrix_ref has a value which is a kb_ke_apps.obj_ref
	workspace_name has a value which is a string
	feature_set_suffix has a value which is a string
	dist_threshold has a value which is a float
	dist_metric has a value which is a string
	linkage_method has a value which is a string
	fcluster_criterion has a value which is a string
obj_ref is a string
EMClusterOutput is a reference to a hash where the following keys are defined:
	feature_set_set_refs has a value which is a reference to a list where each element is a kb_ke_apps.obj_ref
	report_name has a value which is a string
	report_ref has a value which is a string


=end text

=item Description

run_expression_matrix_cluster: generates clusters for ExpressionMatrix data object

=back

=cut

 sub run_expression_matrix_cluster
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function run_expression_matrix_cluster (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to run_expression_matrix_cluster:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'run_expression_matrix_cluster');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ke_apps.run_expression_matrix_cluster",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'run_expression_matrix_cluster',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method run_expression_matrix_cluster",
					    status_line => $self->{client}->status_line,
					    method_name => 'run_expression_matrix_cluster',
				       );
    }
}
 
  
sub status
{
    my($self, @args) = @_;
    if ((my $n = @args) != 0) {
        Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
                                   "Invalid argument count for function status (received $n, expecting 0)");
    }
    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
        method => "kb_ke_apps.status",
        params => \@args,
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
                           code => $result->content->{error}->{code},
                           method_name => 'status',
                           data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
                          );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method status",
                        status_line => $self->{client}->status_line,
                        method_name => 'status',
                       );
    }
}
   

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "kb_ke_apps.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'run_expression_matrix_cluster',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method run_expression_matrix_cluster",
            status_line => $self->{client}->status_line,
            method_name => 'run_expression_matrix_cluster',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for kb_ke_apps::kb_ke_appsClient\n";
    }
    if ($sMajor == 0) {
        warn "kb_ke_apps::kb_ke_appsClient version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 boolean

=over 4



=item Description

A boolean - 0 for false, 1 for true.
@range (0, 1)


=item Definition

=begin html

<pre>
an int
</pre>

=end html

=begin text

an int

=end text

=back



=head2 obj_ref

=over 4



=item Description

An X/Y/Z style reference


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 EMClusterParams

=over 4



=item Description

Input of the run_expression_matrix_cluster function
matrix_ref: Matrix object reference
workspace_name: the name of the workspace
feature_set_suffix: suffix append to FeatureSet object name
dist_threshold: the threshold to apply when forming flat clusters

Optional arguments:
dist_metric: The distance metric to use. Default set to 'euclidean'.
             The distance function can be
             ["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine", 
              "dice", "euclidean", "hamming", "jaccard", "kulsinski", "matching", 
              "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath", "sqeuclidean", 
              "yule"]
             Details refer to:
             https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html

linkage_method: The linkage algorithm to use. Default set to 'ward'.
                The method can be
                ["single", "complete", "average", "weighted", "centroid", "median", "ward"]
                Details refer to:
                https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html

fcluster_criterion: The criterion to use in forming flat clusters. Default set to 'distance'.
                    The criterion can be
                    ["inconsistent", "distance", "maxclust"]
                    Details refer to:
                    https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.fcluster.html


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
matrix_ref has a value which is a kb_ke_apps.obj_ref
workspace_name has a value which is a string
feature_set_suffix has a value which is a string
dist_threshold has a value which is a float
dist_metric has a value which is a string
linkage_method has a value which is a string
fcluster_criterion has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
matrix_ref has a value which is a kb_ke_apps.obj_ref
workspace_name has a value which is a string
feature_set_suffix has a value which is a string
dist_threshold has a value which is a float
dist_metric has a value which is a string
linkage_method has a value which is a string
fcluster_criterion has a value which is a string


=end text

=back



=head2 EMClusterOutput

=over 4



=item Description

Ouput of the run_expression_matrix_cluster function
feature_set_set_refs: a list of result FeatureSetSet object references
report_name: report name generated by KBaseReport
report_ref: report reference generated by KBaseReport


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
feature_set_set_refs has a value which is a reference to a list where each element is a kb_ke_apps.obj_ref
report_name has a value which is a string
report_ref has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
feature_set_set_refs has a value which is a reference to a list where each element is a kb_ke_apps.obj_ref
report_name has a value which is a string
report_ref has a value which is a string


=end text

=back



=cut

package kb_ke_apps::kb_ke_appsClient::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
