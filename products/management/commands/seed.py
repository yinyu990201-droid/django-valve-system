from django.core.management.base import BaseCommand
from products.models import Category, Product, PerformanceCurve

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # Clear existing data
        Category.objects.all().delete()
        Product.objects.all().delete()
        
        # Create Categories
        cat_load_holding = Category.objects.create(name="Load Holding", slug="load-holding", description="Counterbalance valves")
        cat_flow_control = Category.objects.create(name="Flow Control", slug="flow-control", description="Flow control valves")
        
        cat_cb = Category.objects.create(name="Counterbalance", slug="counterbalance", parent=cat_load_holding)
        
        # Create Products
        p1 = Product.objects.create(
            model_code="CBEG-LJN",
            series="Series 1",
            category=cat_cb,
            description="Counterbalance valve with pilot assist",
            cavity="T-11A",
            material="Steel",
            specifications={
                "capacity": "15 gpm (60 L/min)",
                "max_pressure": "5000 psi (350 bar)",
                "pilot_ratio": "3:1"
            }
        )
        
        # Create Performance Curve
        PerformanceCurve.objects.create(
            product=p1,
            curve_type="Pressure Drop",
            data_points=[
                {"x": 0, "y": 0},
                {"x": 10, "y": 50},
                {"x": 20, "y": 120},
                {"x": 30, "y": 200},
            ]
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))
