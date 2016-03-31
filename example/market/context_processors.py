from .models import CartItem

def number_cart_items(request):
    print("context processor opened")
    cur_eve_user = request.user.get_profile()
    return {'number_cart_items':
            len(CartItem.objects.filter(eveuser=cur_eve_user))}
