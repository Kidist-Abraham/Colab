from unittest import TestCase

from git import get_stacks, get_collaborators, validate_git_handle_ownership, validate_repo_existence

class GitFunctionsTestCase(TestCase):
    """Test git functions."""


    def test_get_repo_stack(self):
        """ Does get_stacks function return the languages that are used the repository """

        stacks = get_stacks("Kidist-Abraham/Colab")
        self.assertIn("Python", stacks)


    def test_get_collaborators(self):
        """ Does get_collaborators function return collaborators of a repository"""

        collaborators = get_collaborators("Kidist-Abraham/Colab")
        self.assertIn("Kidist-Abraham", collaborators)


    def test_validate_git_handle_ownership(self):
        """ Does the validate_git_handle_ownership function work as expected"""

        # Should return False if the email is not the same as the owner of the handle
        validate = validate_git_handle_ownership("Kidist-Abraham","kidistabraha@gmail.com",False)
        self.assertFalse(validate)

        # Should return True if the email is the same as the owner of the handle
        validate = validate_git_handle_ownership("Kidist-Abraham","kidistabraham@gmail.com",False)
        self.assertTrue(validate)


    def test_validate_repo_existence(self):
        """ Does the validate_repo_existence function work as expected"""

        # Should return False if the the repo doesn't exist
        exist = validate_repo_existence("Kidist-Abraham/doesn-t-exist")
        self.assertFalse(exist)

        # Should return True if the the repo exists
        exist = validate_repo_existence("Kidist-Abraham/SPI-communication-")
        self.assertTrue(exist)