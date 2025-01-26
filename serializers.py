from rest_framework import serializers

class CommonSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model', None)  # Extract the model from kwargs
        if model:
            self.Meta.model = model  # Dynamically set the model
        super().__init__(*args, **kwargs)

    class Meta:
        model = None  # Default model is None
        fields = '__all__'