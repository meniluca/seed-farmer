#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import hashlib
import logging
from typing import Optional

import humps
import yaml
from boto3 import Session

from seedfarmer.services._service_utils import get_region, get_sts_identity_info

_logger: logging.Logger = logging.getLogger(__name__)

NoDatesSafeLoader = yaml.SafeLoader


class CfnSafeYamlLoader(yaml.SafeLoader):
    """
    CfnSafeYamlLoader
    A predefined class loader to support safely reading YAML files

    Parameters
    ----------
    yaml : _type_
    """

    yaml_implicit_resolvers = {
        k: [r for r in v if r[0] != "tag:yaml.org,2002:timestamp"]
        for k, v in NoDatesSafeLoader.yaml_implicit_resolvers.items()
    }


def upper_snake_case(value: str) -> str:
    """
    This will convert strings to a standard format

    Parameters
    ----------
    value : str
        The string you want to convert

    Returns
    -------
    str
        the string standardized
    """
    if humps.is_camelcase(value):  # type: ignore
        return humps.decamelize(value).upper()  # type: ignore
    elif humps.is_pascalcase(value):  # type: ignore
        return humps.depascalize(value).upper()  # type: ignore
    else:
        return value.replace("-", "_").upper()


def generate_hash(string: str, length: int = 8) -> str:
    return (hashlib.sha1(string.encode("UTF-8")).hexdigest())[:length]


def generate_session_hash(session: Optional[Session] = None) -> str:
    """
    Generate a hexdigest hash of the project and the deployment - for use generating unique names

    Returns
    -------
    str
        The resulting hash as a string
    """
    account, _, _ = get_sts_identity_info(session=session)
    region = get_region(session=session)
    concatenated_string = f"{account}-{region}"
    hash_value = generate_hash(string=concatenated_string, length=8)
    _logger.debug("HASH generated is %s", hash_value)
    return hash_value


def generate_codebuild_url(account_id: str, region: str, codebuild_id: str, partition: Optional[str] = "aws") -> str:
    """
    Generate a standard URL for codebuild build information

    Parameters
    ----------
    account_id : str
        The AWS account id where CodeBuild ran
    region : str
        The AWS region where CodeBuild ran
    codebuild_id : str
        The CodeBuild Build ID

    Returns
    -------
    str
        The standard URL with protocol and query parameters
        ex: https://us-east-1.console.aws.amazon.com/codesuite/codebuild/123456789012/projects/
            codebuild-id/build/codebuild-id:3413241234/?region-us-east-1
        if in a differeing partion (ex.aws-cn) the url looks like:
            https://cn-north-1.console.amazonaws.cn/codesuite/codebuild/123456789012/projects/
            codeseeder-idf/build/codeseeder-id:3413241234/?region=cn-north-1
    """
    try:
        b_id_enc = codebuild_id.replace(":", "%3A")
        cb_p = codebuild_id.split(":")[0]
        domain_completion = ".console.aws.amazon.com/codesuite/codebuild/"
        if partition == "aws-cn":
            domain_completion = ".console.amazonaws.cn/codesuite/codebuild/"
        return "".join(
            (
                "https://",
                f"{region}",
                f"{domain_completion}",
                f"{account_id}",
                "/projects/",
                f"{cb_p}",
                "/build/",
                f"{b_id_enc}",
                "/?region=",
                f"{region}",
            )
        )
    except Exception as e:
        _logger.error(f"Error...{account_id} - {region} - {codebuild_id} - {e} ")
        return "N/A"


def get_toolchain_role_name(project_name: str, qualifier: Optional[str] = None) -> str:
    name = f"seedfarmer-{project_name}-toolchain-role"
    return f"{name}-{qualifier}" if qualifier else name


def get_toolchain_role_arn(
    partition: str, toolchain_account_id: str, project_name: str, qualifier: Optional[str] = None
) -> str:
    return f"arn:{partition}:iam::{toolchain_account_id}:role/{get_toolchain_role_name(project_name,qualifier)}"


def get_deployment_role_name(project_name: str, qualifier: Optional[str] = None) -> str:
    name = f"seedfarmer-{project_name}-deployment-role"
    return f"{name}-{qualifier}" if qualifier else name


def get_deployment_role_arn(
    partition: str, deployment_account_id: str, project_name: str, qualifier: Optional[str] = None
) -> str:
    return f"arn:{partition}:iam::{deployment_account_id}:role/{get_deployment_role_name(project_name,qualifier)}"


def valid_qualifier(qualifer: str) -> bool:
    return True if ((len(qualifer) <= 6) and qualifer.isalnum()) else False
