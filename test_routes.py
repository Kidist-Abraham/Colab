from unittest import TestCase


from models import db, connect_db, User, Sector, Project, SECTORS

from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///colab-test"
app.config['SQLALCHEMY_ECHO'] = False
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

CURR_USER_KEY = "username"

class ViewTestCase(TestCase):
    """Test routes."""

    @classmethod
    def setUpClass(cls):
        "Populate Sector DB"

        Sector.add_stacks_to_db()
        

    def setUp(self):
        """Create test client, add sample data."""

        self.sector_id = 2
        Project.query.delete()
        User.query.delete()
        
        

        self.client = app.test_client()

        self.testuser = User.register(username="kid",
                                    email="kidistabraham@gmail.com",
                                    password="testuser",
                                    first_name = "Kidist", 
                                    last_name="Abraham", 
                                    git_handle="Kidist-Abraham",
                                    is_organisation= False)

        db.session.add(self.testuser)
        db.session.commit()

        self.testproject_ = {"title": "Test title", 
                            "git_repo":"Kidist-Abraham/internAt",
                            "description": "description", 
                            "owned_by": self.testuser.username, 
                            "sector_id": self.sector_id

        }

        self.testproject = Project(**self.testproject_)
        
        db.session.add(self.testproject)


        db.session.commit()
        self.testproject_["id"] = self.testproject.id

    def test_show_homepge(self):
        """Can the '/' route show home page when a user is logged in """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username
                # print("***************", sess[CURR_USER_KEY])

            # Now, that session setting is saved, so we can have
            # the rest of ours test
  
            resp = c.get("/", follow_redirects= True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"Add Project", html)


    def test_show_profile(self):
        """Can the '/profile' route show user's profile"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username

            resp = c.get(f"/profile", follow_redirects= True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuser.first_name, html)


    def test_delete_user(self):
        """Can the '/users/delete' route delete user"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username

            resp = c.post(f"/users/{self.testuser.username}/delete", follow_redirects= True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", html)


    def test_delete_user(self):
        """Can the '/users/<username>/delete' route delete user"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username

            resp = c.post(f"/users/{self.testuser.username}/delete", follow_redirects= True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", html)


    def test_edit_user(self):
        """Can the '/users/<username>/edit' route delete user"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username

            resp = c.post(f"/users/{self.testuser.username}/edit", data ={"first_name":"Kidist Abraham"}, follow_redirects= True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Kidist Abraham", html)


    def test_add_project(self):
        """Can the 'users/<username>/projects/add' route add project"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username

            
            
            resp = c.post(f"/users/{self.testuser.username}/projects/add", data ={"title": "title", "git_repo": "Kidist-Abraham/Colab", "description":"description", "sector": self.sector_id}, follow_redirects= True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You created new project", html)


    def test_show_project(self):
        """Can the '/projects/<project_id>' route show project"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username
            
            resp = c.get(f"/projects/{self.testproject_['id']}", follow_redirects= True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testproject_["git_repo"], html)

    def test_show_projects(self):
        """Can the '/projects' route show all project except the ones owned by the user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username

            testuser2 = User.register(username="IO",
                                    email="contact@iohk.io",
                                    password="testuser",
                                    first_name = "IO", 
                                    last_name="HK", 
                                    git_handle="input-output-hk",
                                    is_organisation= True)

            db.session.add(testuser2)
            db.session.commit()

            testproject2_ = {"title": "Project 2 ", 
                            "git_repo":"input-output-hk/cardano-node",
                            "description": "description", 
                            "owned_by": testuser2.username, 
                            "sector_id": self.sector_id

             }

            testproject2 = Project(**testproject2_)
            
            db.session.add(testproject2)


            db.session.commit()
            testproject2_["id"] = testproject2.id
                
            resp = c.get(f"/projects", follow_redirects= True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)

            # /projects should show projects created by other users
            self.assertIn(testproject2_["title"], html)

            # /projects should not show projects created by the user
            self.assertNotIn(self.testproject_["title"], html)



    def test_show_owned_projects(self):
        """Can the '/owned-projects'route show all project owned by the logged in user and not other users"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username

            testuser2 = User.register(username="IO",
                                    email="contact@iohk.io",
                                    password="testuser",
                                    first_name = "IO", 
                                    last_name="HK", 
                                    git_handle="input-output-hk",
                                    is_organisation= True)

            db.session.add(testuser2)
            db.session.commit()

            testproject2_ = {"title": "Project 2 ", 
                            "git_repo":"input-output-hk/cardano-node",
                            "description": "description", 
                            "owned_by": testuser2.username, 
                            "sector_id": self.sector_id

             }

            testproject2 = Project(**testproject2_)
            
            db.session.add(testproject2)


            db.session.commit()
            testproject2_["id"] = testproject2.id
                
            resp = c.get(f"/owned-projects", follow_redirects= True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)

            # /projects should show projects created by the logged in user
            self.assertIn(self.testproject_["title"], html)

            # /projects should not show projects created by the user
            self.assertNotIn(testproject2_["title"], html)


    

    
    def test_delete_project(self):
        """Can the '/projects/<project_id>/delete' route delete project"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username

            resp = c.post(f"/projects/{self.testproject_['id']}/delete", follow_redirects= True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(self.testproject_['title'], html)


    def test_edit_project(self):
        """Can the '/projects/<project_id>/edit' route edit project"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.username

            resp = c.post(f"/projects/{self.testproject_['id']}/update", data ={"title":"Hero"}, follow_redirects= True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hero", html)

   