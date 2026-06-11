from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from engine.llm_compiler import generate_schema_from_prompt, create_api_from_schema

class Command(BaseCommand):
    help = "Generate a live dynamic API from a natural language prompt"

    def add_arguments(self, parser):
        parser.add_argument('prompt', type=str, help='The natural language description of the API you want')
    
    def handle(self, *args, **options):
        prompt = options['prompt']

        owner = User.objects.filter(is_superuser=True).first()
        if not owner:
            self.stdout.write(self.style.ERROR('No superuser found. Please create one first using createsuperuser.'))
            return
        
        self.stdout.write(self.style.WARNING(f"Analyzing prompt: '{prompt}'..."))

        try:
            schema = generate_schema_from_prompt(prompt)
            self.stdout.write(self.style.SUCCESS(f"Schema Generated: {schema.api_name}({schema.api_slug})"))
            for f in schema.fields:
                self.stdout.write(f"  - {f.field_name} ({f.data_type})")
            
            self.stdout.write(self.style.WARNING("Building PostgreSQL table..."))
            api_record = create_api_from_schema(schema, owner, prompt)

            self.stdout.write(self.style.SUCCESS(f"\nSuccess! API is live at:"))
            
            self.stdout.write(self.style.SUCCESS(f"http://127.0.0.1:8000/api/v1/dynamic/{api_record.slug}/"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to generate API: {str(e)}"))