from django.core.management.base import BaseCommand
from products.models import Category, CartridgeValve, ValveDocument
from django.core.files.base import ContentFile
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Seeds database with Chinese test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        CartridgeValve.objects.all().delete()
        Category.objects.all().delete()
        ValveDocument.objects.all().delete()

        self.stdout.write('Creating categories...')
        
        # Root Categories
        cartridge_valves = Category.objects.create(name='插装阀', slug='cartridge-valves', description='各类高品质插装阀')
        
        # Sub Categories
        dir_valves = Category.objects.create(name='方向控制阀', slug='directional-valves', parent=cartridge_valves)
        flow_valves = Category.objects.create(name='流量控制阀', slug='flow-valves', parent=cartridge_valves)
        press_valves = Category.objects.create(name='压力控制阀', slug='pressure-valves', parent=cartridge_valves)
        load_valves = Category.objects.create(name='负载控制阀', slug='load-control-valves', parent=cartridge_valves)

        self.stdout.write('Creating products...')
        
        products_data = [
            {
                'category': dir_valves,
                'series': 'DD-21A-44',
                'name': '二位二通电磁阀 (常闭)',
                'description': '先导式二位二通电磁方向控制阀，常闭型。适用于低泄漏应用。',
                'max_pressure': 350,
                'max_flow': 60,
                'cavity': 'T-11A',
                'material': '钢',
                'application': '工程机械, 农业机械'
            },
             {
                'category': dir_valves,
                'series': 'DD-21A-45',
                'name': '二位二通电磁阀 (常开)',
                'description': '先导式二位二通电磁方向控制阀，常开型。',
                'max_pressure': 315,
                'max_flow': 50,
                'cavity': 'T-11A',
                'material': '钢',
                'application': '一般液压系统'
            },
            {
                'category': dir_valves,
                'series': 'DT-13A-51',
                'name': '双向双锁手动阀',
                'description': '手动操作的双向截止阀，用于锁定执行机构。',
                'max_pressure': 250,
                'max_flow': 40,
                'cavity': 'T-13A',
                'material': '铝合金',
                'application': '手动液压设备'
            },
            {
                'category': flow_valves,
                'series': 'FC-10',
                'name': '针阀 (流量控制)',
                'description': '精密调节流量的针形阀，带反向自由流。',
                'max_pressure': 210,
                'max_flow': 30,
                'cavity': 'T-10A',
                'material': '不锈钢',
                'application': '速度控制回路'
            },
             {
                'category': press_valves,
                'series': 'RV-08',
                'name': '直动式溢流阀',
                'description': '快速响应的直动式溢流阀，用于系统过压保护。',
                'max_pressure': 400,
                'max_flow': 20,
                'cavity': 'T-08A',
                'material': '钢',
                'application': '保护回路'
            },
            {
                'category': load_valves,
                'series': 'CB-10',
                'name': '平衡阀',
                'description': '用于控制负载下降速度并提供软管爆裂保护。',
                'max_pressure': 350,
                'max_flow': 60,
                'cavity': 'T-11A',
                'material': '钢',
                'application': '起重机, 挖掘机'
            }
        ]

        for p_data in products_data:
            CartridgeValve.objects.create(**p_data)
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded database with Chinese data!'))
