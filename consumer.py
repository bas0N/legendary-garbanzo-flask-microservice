import os
import pika,json
from os.path import join, dirname
from app import Product, db
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
print("the path is", dotenv_path)
load_dotenv(dotenv_path)
rabbit_mq_url = os.environ.get('RABBITMQ')

if(rabbit_mq_url is None):
    raise Exception("RABBITMQ not found in environment variables")

params = pika.URLParameters(rabbit_mq_url)

connection = pika.BlockingConnection(params)
if(connection.is_open):
    print('Connection opened')
else:
    print('Connection error')
channel = connection.channel()

channel.queue_declare(queue='main')


def callback(ch, method, properties, body):
    print('Received in main')
    data = json.loads(body)
    print(data)

    if(properties.content_type == 'product_created'):
        print('Product created')
        product = Product(id=data['id'],title=data['title'],image=data['image'])
        db.session.add(product)
        db.session.commit()
        print('Product saved')
    elif(properties.content_type == 'product_updated'):
        print('Product updated')
        product = Product.query.get(data['id'])
        product.title = data['title']
        product.image = data['image']
        db.session.commit()

        print('Product updated')
    elif(properties.content_type == 'product_deleted'):
        print('Product deleted')
        product = Product.query.get(data)
        db.session.delete(product)
        db.session.commit()
        print('Product deleted')


channel.basic_consume(queue='main', on_message_callback=callback,auto_ack=True)

print('Started Consuming messages')

channel.start_consuming()

channel.close()

