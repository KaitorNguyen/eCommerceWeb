from rest_framework import serializers
from .models import User, Category, Shop, Product, Tag, Comment, Review, Notification
from django.db.models import Avg, Q


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        data = validated_data.copy()
        # {'first_name':'abc'}
        # u = User(first_name=data['first_name'])
        u = User(**data)
        if not u.avatar:
            u.avatar = "/default/avatar_default_pgdx3q.jpg"
        if u.role == 'Seller':
            u.is_verified = False
        u.set_password(u.password)
        u.save()

        if u.role == 'Seller':
            recipients = User.objects.filter(Q(is_staff=True) | Q(role='Employee')).all()
            for recipient in recipients:
                notice = Notification(sender=u.id, content="Đăng kí trở thành nhà bán hàng - {}".format(u.username),
                                      recipient=recipient)
                notice.save()
        return u

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'avatar', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class ConfirmUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'is_verified']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'avatar', 'description']

class ShopDetailSerializer(ShopSerializer):
    product_count = serializers.SerializerMethodField(read_only=True)

    def get_product_count(self, obj):
        return Product.objects.filter(shop=obj).count()

    class Meta:
        model = ShopSerializer.Meta.model
        fields = ShopSerializer.Meta.fields + ['created_date', 'is_active', 'product_count']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image']

class ProductDetailSerializer(ProductSerializer):
    category = CategorySerializer()
    shop = ShopSerializer()
    tags = TagSerializer(many=True)

    avg_rate = serializers.SerializerMethodField()
    total_review = serializers.SerializerMethodField()
    total_comment = serializers.SerializerMethodField()

    def get_avg_rate(self, product):
        avg_rate = product.review_set.aggregate(Avg('rate'))['rate__avg']
        return int(avg_rate) if avg_rate else 0
    def get_total_review(self, product):
        return product.review_set.count()
    def get_total_comment(self, product):
        return product.comment_set.count()

    class Meta:
        model = ProductSerializer.Meta.model
        fields = ProductSerializer.Meta.fields + ['description', 'shop', 'category', 'tags', 'avg_rate', 'total_review', 'total_comment']
        extra_kwargs = {
            'avg_rate': {'read_only': True},
            'total_review': {'read_only': True},
            'total_comment': {'read_only': True}
        }

class ProductUpdateNoTagSerializer(ProductSerializer):
    category = CategorySerializer()
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = ProductSerializer.Meta.model
        fields = ProductSerializer.Meta.fields + ['description', 'shop', 'category']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    def validate_rate(self, rate):
        if rate < 0 or rate > 5:
            raise serializers.ValidationError('Giá trị rate phải nằm trong khoảng từ 0 đến 5')
        return rate

    class Meta:
        model = Review
        fields = ['id', 'rate', 'content', 'created_date', 'updated_date', 'user']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    replies = serializers.SerializerMethodField()

    def get_replies(self, obj):
        replies = Comment.objects.filter(reply_to=obj)
        serializer = CommentSerializer(replies, many=True)
        return serializer.data

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_date', 'user', 'reply_to', 'replies']

class UpdateCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_date', 'updated_date', 'user']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'