from rest_framework import serializers

class EnableMFASerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=["totp", "sms"])


class VerifyMFASerializer(serializers.Serializer):
    code = serializers.CharField()


class MFAEnableSerializer(serializers.Serializer):
    pass


class MFAVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


class MFADisableSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
