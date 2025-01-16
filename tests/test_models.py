# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """Test to read a product"""
        try:
            product = ProductFactory()
            product.id = None
            product.create()
            app.logger.info(f"Create product: {product}")
            self.assertIsNotNone(product.id)
            # fetch
            fetched_product = Product.find(product.id)
            self.assertEqual(product.name, fetched_product.name)
            self.assertEqual(product.description, fetched_product.description)
            self.assertEqual(product.available, fetched_product.available)
            self.assertEqual(product.category, fetched_product.category)
            self.assertEqual(product.price, fetched_product.price)
        except Exception as e:
            app.logger.error(f"Create product failed {e}")

    def test_update_a_product(self):
        """Test to update a product"""
        try:
            product = ProductFactory()
            product.id = None
            product.create()
            app.logger.info(f"Create product: {product}")
            self.assertIsNotNone(product.id)
            # update the product description
            product.description = "test description"
            original_id = product.id
            product.update()
            self.assertEqual(product.id, original_id)
            self.assertEqual(product.description, "test description")
            # fetch
            products = Product.all()
            self.assertEqual(len(products), 1)
            fetched_product = products[0]
            self.assertEqual(fetched_product.id, original_id)
            self.assertEqual(fetched_product.description, "test description")
            product = ProductFactory()
            product.id = None
            self.assertRaises(DataValidationError, product.update)
        except Exception as e:
            app.logger.error(f"Create product failed {e}")

    def test_delete_a_product(self):
        """Test to delete a product"""
        try:
            product = ProductFactory()
            product.id = None
            product.create()
            app.logger.info(f"Create product: {product}")
            self.assertIsNotNone(product.id)
            # fetch
            self.assertEqual(len(Product.all()), 1)
            product.delete()
            self.assertEqual(len(Product.all()), 0)
        except Exception as e:
            app.logger.error(f"Create product failed {e}")

    def test_list_all_product(self):
        """Test to list all products"""
        try:
            products = Product.all()
            self.assertEqual(len(products), 0)
            # create 5 products
            for i in range(5):
                product = ProductFactory()
                product.id = None
                product.create()
                app.logger.info(f"Creating product #{i} {product}")
                self.assertIsNotNone(product.id)
            # fetch
            self.assertEqual(len(Product.all()), 5)
        except Exception as e:
            app.logger.error(f"Create product failed {e}")

    def test_search_a_product_by_name(self):
        """Test searching a product by name"""
        try:
            # create 5 products
            products = ProductFactory.create_batch(5)
            for product in products:
                product.create()
                app.logger.info(f"Creating product {product}")
            self.assertEqual(len(Product.all()), 5)
            # find by name
            first_product_name = products[0].name
            products_with_same_name = Product.find_by_name(first_product_name)
            product_count = len([prod for prod in products if prod.name == first_product_name])
            self.assertEqual(len(products_with_same_name), product_count)

        except Exception as e:
            app.logger.error(f"Create product failed {e}")

    def test_search_a_product_by_category(self):
        """Test searching a product by category"""
        try:
            # create 10 products
            products = ProductFactory.create_batch(10)
            for product in products:
                product.create()
                app.logger.info(f"Creating product {product}")
            self.assertEqual(len(Product.all()), 10)
            # find by category
            first_product_category = products[0].category
            products_with_same_category = Product.find_by_category(first_product_category)
            product_count = len([prod for prod in products if prod.category == first_product_category])
            self.assertEqual(len(products_with_same_category), product_count)

        except Exception as e:
            app.logger.error(f"Create product failed {e}")

    def test_search_a_product_by_availability(self):
        """Test searching a product by availability"""
        try:
            # create 10 products
            products = ProductFactory.create_batch(10)
            for product in products:
                product.create()
                app.logger.info(f"Creating product {product}")
            self.assertEqual(len(Product.all()), 10)
            # find by availability
            first_product_availability = products[0].available
            products_with_same_availability = Product.find_by_availability(first_product_availability)
            product_count = len([prod for prod in products if prod.available == first_product_availability])
            self.assertEqual(len(products_with_same_availability), product_count)

        except Exception as e:
            app.logger.error(f"Create product failed {e}")

    def test_search_a_product_by_price(self):
        """Test searching a product by price"""
        try:
            # create 10 products
            products = ProductFactory.create_batch(10)
            for product in products:
                product.create()
                app.logger.info(f"Creating product {product}")
            self.assertEqual(len(Product.all()), 10)
            # find by price
            first_product_price = products[0].price
            products_with_same_price = Product.find_by_price(first_product_price)
            product_count = len([prod for prod in products if prod.price == first_product_price])
            self.assertEqual(len(products_with_same_price), product_count)

        except Exception as e:
            app.logger.error(f"Create product failed {e}")

    def test_product_serialize_deserialise(self):
        """Test product serialize deserialise"""
        product = ProductFactory()
        product.id = None
        product.create()
        product_data = product.serialize()
        product_data["available"] = "not_valid"
        self.assertRaises(DataValidationError, product.deserialize, product_data)
        self.assertRaises(DataValidationError, product.deserialize, {})
        del product_data["name"]
        self.assertRaises(DataValidationError, product.deserialize, product_data)
        self.assertRaises(DataValidationError, product.deserialize, None)
