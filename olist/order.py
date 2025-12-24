import pandas as pd
import numpy as np
from olist.utils import haversine_distance
from olist.data import Olist


class Order:
    '''
    DataFrames containing all orders as index,
    and various properties of these orders as columns
    '''
    def __init__(self):
        # Assign an attribute ".data" to all new instances of Order
        self.data = Olist().get_data()

    def get_wait_time(self, is_delivered=True):
        """
        Returns a DataFrame with:
        [order_id, wait_time, expected_wait_time, delay_vs_expected, order_status]
        and filters out non-delivered orders unless specified
        """
        # Hint: Within this instance method, you have access to the instance of the class Order in the variable self, as well as all its attributes
        orders = self.data['orders'].copy()
        orders = orders[orders['order_status'] == 'delivered']
        date_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
             'order_delivered_customer_date', 'order_estimated_delivery_date']
        for col in date_cols:
          orders[col] = pd.to_datetime(orders[col])
    
        orders["wait_time"] = ((orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]).dt.total_seconds() / 86400)
        orders["expected_wait_time"] = ((orders["order_estimated_delivery_date"] - orders["order_purchase_timestamp"]).dt.total_seconds() / 86400)
        orders["delay_vs_expected"] = orders["wait_time"] - orders["expected_wait_time"]
        orders.loc[orders['delay_vs_expected'] < 0, 'delay_vs_expected'] = 0
        
        return orders[['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected', 'order_status']]

    def get_review_score(self):
        """
        Returns a DataFrame with:
        order_id, dim_is_five_star, dim_is_one_star, review_score
        """
        reviews = self.data['order_reviews'].copy()
        def check_rate(score):
            if score == 5:
                return 1
            else:
                return 0
        def check_rate_1(score):
            if score == 1:
                return 0
            else:
                return 1    
        reviews["dim_is_five_star"] = reviews["review_score"].apply(check_rate)
        reviews["dim_is_one_star"] = reviews["review_score"].apply(check_rate_1)
        return reviews[['order_id', 'dim_is_five_star', 'dim_is_one_star', 'review_score']]

    def get_number_items(self):
        """
        Returns a DataFrame with:
        order_id, number_of_items
        """
        order_items = self.data['order_items'].copy()
        nb_of_items = order_items.groupby('order_id')['order_id'].count().reset_index(name='number_of_items')
        return nb_of_items
    
    def get_number_sellers(self):
        """
        Returns a DataFrame with:
        order_id, number_of_sellers
        """
        orders_items = self.data['order_items'].copy()
        nb_of_sellers = orders_items.groupby('order_id')['seller_id'].nunique().reset_index(name='number_of_sellers')
        return nb_of_sellers

    def get_price_and_freight(self):
        """
        Returns a DataFrame with:
        order_id, price, freight_value
        """
        orders_items = self.data['order_items'].copy()
        price_and_freight = orders_items.groupby('order_id').agg({'price':'sum', 'freight_value':'sum'}).reset_index()
        return price_and_freight

    # Optional
    def get_distance_seller_customer(self):
        """
        Returns a DataFrame with:
        order_id, distance_seller_customer
        """
        pass  # YOUR CODE HERE

    def get_training_data(self, is_delivered=True, with_distance_seller_customer=False):
        """
        Tüm özellikleri tek bir DataFrame'de toplar ve modellemeye hazır hale getirir.
        """
        # 1. Ana iskeleti oluştur (Wait Time tablosu filtreli olduğu için bunu baz alıyoruz)
        training_data = self.get_wait_time(is_delivered=is_delivered)
        
        # 2. Diğer özellikleri çağır
        reviews = self.get_review_score()
        products = self.get_number_items()
        sellers = self.get_number_sellers()
        price = self.get_price_and_freight()
        
        # 3. Birleştirme (Merge)
        # 'how' belirtmezsek pandas varsayılan olarak 'inner' join yapar.
        # Yani sadece her iki tabloda da olan order_id'leri tutar.
        training_data = training_data.merge(reviews, on='order_id')
        training_data = training_data.merge(products, on='order_id')
        training_data = training_data.merge(sellers, on='order_id')
        training_data = training_data.merge(price, on='order_id')
        
        # (Opsiyonel) Mesafe hesabı istenirse onu da ekle (Henüz yazmadıysan burası çalışmaz ama iskelette kalsın)
        if with_distance_seller_customer:
            distance = self.get_distance_seller_customer()
            training_data = training_data.merge(distance, on='order_id')
        
        # 4. Temizlik (Drop NaN)
        # Modeller boş değer sevmez, bu yüzden eksik satırları atıyoruz.
        return training_data.dropna()
