#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Tests for the package."""

# pylint: disable=line-too-long

import os
import sys
import unittest

from . import TestDetails

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import simple_ado  # pylint: disable=wrong-import-order


class LibraryTests(unittest.TestCase):
    """Basic tests."""

    def setUp(self) -> None:
        """Set up method."""
        self.test_config = TestDetails()
        self.client = simple_ado.ADOClient(
            tenant=self.test_config.tenant,
            credentials=(self.test_config.username, self.test_config.token),
        )

    def test_get_blobs(self):
        """Test get blobs."""
        self.client.git.get_blobs(
            blob_ids=[
                "7351cd0c84377c067602e97645e9c91100c38a6e",
                "bcb7f5028bf4f26a005d315a4863670e3125c262",
            ],
            output_path=os.path.expanduser("~/Downloads/blobs.zip"),
            repository_id=self.test_config.repository_id,
        )

    def test_get_blob(self):
        """Test get blob."""
        diff = self.client.git.get_blob(
            blob_id="7351cd0c84377c067602e97645e9c91100c38a6e",
            blob_format=simple_ado.git.ADOGitClient.BlobFormat.text,
            repository_id=self.test_config.repository_id,
        )
        print(diff)

    def test_git_diff(self):
        """Test git diff."""
        all_prs = self.client.list_all_pull_requests(repository_id=self.test_config.repository_id)
        details = all_prs[0]
        diff = self.client.git.diff_between_commits(
            base_commit=details["lastMergeTargetCommit"]["commitId"],
            target_commit=details["lastMergeSourceCommit"]["commitId"],
            repository_id=self.test_config.repository_id,
        )
        assert len(diff["changes"]) > 0

    def test_properties(self):
        """Test get properties."""
        all_prs = self.client.list_all_pull_requests(repository_id=self.test_config.repository_id)
        latest_pr = all_prs[0]
        pr_id = latest_pr["pullRequestId"]
        pr_id = 441259
        base_properties = self.client.pull_request(
            pr_id, self.test_config.repository_id
        ).get_properties()
        base_count = len(base_properties)
        new_properties = self.client.pull_request(
            pr_id, self.test_config.repository_id
        ).add_property("Hello", "World")
        self.assertEqual(base_count + 1, len(new_properties))
        after_deletion = self.client.pull_request(
            pr_id, self.test_config.repository_id
        ).delete_property("Hello")
        self.assertEqual(len(after_deletion), base_count)
        print("Done")

    def test_list_repos(self):
        """Test list repos."""
        repos = self.client.git.all_repositories()
        self.assertTrue(len(repos) > 0, "Failed to find any repos")

    def test_list_refs(self):
        """Test list refs."""
        refs = self.client.git.get_refs(repository_id=self.test_config.repository_id)
        self.assertTrue(len(refs) > 0, "Failed to find any refs")

    def test_get_commit(self):
        """Test get commit."""
        refs = self.client.git.get_refs(repository_id=self.test_config.repository_id)
        ref = refs[0]
        commit_id = ref["objectId"]
        commit = self.client.git.get_commit(
            commit_id=commit_id, repository_id=self.test_config.repository_id
        )
        self.assertIsNotNone(commit)

    # TODO: We can't test this until we can also create branches
    # def test_delete_branch(self):
    #    """Test delete branch."""
    #    response = self.client.git.delete_branch("refs/heads/?", "?")
    #    for value in response:
    #        self.assertTrue(value["success"])

    def test_get_pull_requests(self):
        """Test get pull requests."""
        refs = self.client.list_all_pull_requests(repository_id=self.test_config.repository_id)
        self.assertTrue(len(refs) > 0)

    def test_get_pools(self):
        """Test get pools."""
        response = self.client.pools.get_pools()
        self.assertGreater(len(response), 0)

    def test_capabilities(self):
        """Test setting capabilities."""
        pool = self.client.pools.get_pools(
            action_filter=simple_ado.pools.TaskAgentPoolActionFilter.manage
        )[0]
        agent = self.client.pools.get_agents(pool_id=pool["id"])[0]
        capabilities = agent["userCapabilities"]
        capabilities["hello"] = "world"
        self.client.pools.update_agent_capabilities(
            pool_id=pool["id"], agent_id=agent["id"], capabilities=capabilities
        )
