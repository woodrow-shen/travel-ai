"""SQLAdmin configuration — dev/ops database browser.

Mounted at /admin when ADMIN_ENABLED=true (default in development).
"""

from sqladmin import Admin, ModelView

from app.models.activity import Activity
from app.models.chat_session import ChatSession
from app.models.flight import Flight
from app.models.hotel import Hotel
from app.models.itinerary import Itinerary
from app.models.notification_log import NotificationLog
from app.models.price_history import PriceHistory
from app.models.subscription import Subscription, SubscriptionEmail
from app.models.trip import Trip
from app.models.user import User, UserPreference


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.name, User.tier, User.last_login, User.created_at]
    column_searchable_list = [User.email, User.name]
    column_sortable_list = [User.email, User.tier, User.created_at, User.last_login]
    column_default_sort = ("created_at", True)
    page_size = 50
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"


class UserPreferenceAdmin(ModelView, model=UserPreference):
    column_list = [
        UserPreference.id, UserPreference.user_id,
        UserPreference.home_airports, UserPreference.preferred_airlines,
        UserPreference.max_stops, UserPreference.created_at,
    ]
    page_size = 50
    name = "User Preference"
    name_plural = "User Preferences"
    icon = "fa-solid fa-sliders"


class TripAdmin(ModelView, model=Trip):
    column_list = [
        Trip.id, Trip.user_id, Trip.title, Trip.destination,
        Trip.start_date, Trip.end_date, Trip.created_at,
    ]
    column_searchable_list = [Trip.title, Trip.destination]
    column_sortable_list = [Trip.title, Trip.start_date, Trip.created_at]
    column_default_sort = ("created_at", True)
    page_size = 50
    name = "Trip"
    name_plural = "Trips"
    icon = "fa-solid fa-plane-departure"


class FlightAdmin(ModelView, model=Flight):
    column_list = [
        Flight.id, Flight.origin, Flight.destination, Flight.airline,
        Flight.flight_no, Flight.price_amount, Flight.price_currency,
        Flight.departure, Flight.source, Flight.created_at,
    ]
    column_searchable_list = [Flight.origin, Flight.destination, Flight.airline]
    column_sortable_list = [
        Flight.origin, Flight.destination, Flight.price_amount,
        Flight.departure, Flight.created_at,
    ]
    column_default_sort = ("created_at", True)
    page_size = 50
    name = "Flight"
    name_plural = "Flights"
    icon = "fa-solid fa-plane"


class HotelAdmin(ModelView, model=Hotel):
    column_list = [
        Hotel.id, Hotel.name, Hotel.location, Hotel.stars,
        Hotel.price_per_night, Hotel.price_currency,
        Hotel.check_in, Hotel.source, Hotel.created_at,
    ]
    column_searchable_list = [Hotel.name, Hotel.location]
    column_sortable_list = [Hotel.name, Hotel.price_per_night, Hotel.created_at]
    column_default_sort = ("created_at", True)
    page_size = 50
    name = "Hotel"
    name_plural = "Hotels"
    icon = "fa-solid fa-hotel"


class ActivityAdmin(ModelView, model=Activity):
    column_list = [
        Activity.id, Activity.name, Activity.location, Activity.category,
        Activity.price_amount, Activity.price_currency, Activity.created_at,
    ]
    column_searchable_list = [Activity.name, Activity.location]
    column_default_sort = ("created_at", True)
    page_size = 50
    name = "Activity"
    name_plural = "Activities"
    icon = "fa-solid fa-map-pin"


class ItineraryAdmin(ModelView, model=Itinerary):
    column_list = [Itinerary.id, Itinerary.trip_id, Itinerary.title, Itinerary.created_at]
    column_searchable_list = [Itinerary.title]
    column_default_sort = ("created_at", True)
    page_size = 50
    name = "Itinerary"
    name_plural = "Itineraries"
    icon = "fa-solid fa-route"


class ChatSessionAdmin(ModelView, model=ChatSession):
    column_list = [ChatSession.id, ChatSession.user_id, ChatSession.title, ChatSession.created_at]
    column_searchable_list = [ChatSession.title]
    column_default_sort = ("created_at", True)
    page_size = 50
    name = "Chat Session"
    name_plural = "Chat Sessions"
    icon = "fa-solid fa-comments"


class PriceHistoryAdmin(ModelView, model=PriceHistory):
    column_list = [
        PriceHistory.id, PriceHistory.origin, PriceHistory.destination,
        PriceHistory.departure_date, PriceHistory.airline,
        PriceHistory.price_amount, PriceHistory.price_currency,
        PriceHistory.source, PriceHistory.stops, PriceHistory.created_at,
    ]
    column_searchable_list = [PriceHistory.origin, PriceHistory.destination, PriceHistory.airline]
    column_sortable_list = [
        PriceHistory.origin, PriceHistory.destination,
        PriceHistory.price_amount, PriceHistory.departure_date, PriceHistory.created_at,
    ]
    column_default_sort = ("created_at", True)
    page_size = 100
    name = "Price History"
    name_plural = "Price History"
    icon = "fa-solid fa-chart-line"


class SubscriptionAdmin(ModelView, model=Subscription):
    column_list = [
        Subscription.id, Subscription.user_id, Subscription.email_id,
        Subscription.type, Subscription.is_active, Subscription.config,
        Subscription.last_sent_at, Subscription.created_at,
    ]
    column_sortable_list = [Subscription.type, Subscription.is_active, Subscription.created_at]
    column_default_sort = ("created_at", True)
    page_size = 50
    name = "Subscription"
    name_plural = "Subscriptions"
    icon = "fa-solid fa-bell"


class SubscriptionEmailAdmin(ModelView, model=SubscriptionEmail):
    column_list = [
        SubscriptionEmail.id, SubscriptionEmail.user_id, SubscriptionEmail.email,
        SubscriptionEmail.is_verified, SubscriptionEmail.verified_at, SubscriptionEmail.created_at,
    ]
    column_searchable_list = [SubscriptionEmail.email]
    column_sortable_list = [
        SubscriptionEmail.email, SubscriptionEmail.is_verified,
        SubscriptionEmail.created_at,
    ]
    column_default_sort = ("created_at", True)
    page_size = 50
    name = "Subscription Email"
    name_plural = "Subscription Emails"
    icon = "fa-solid fa-envelope"


class NotificationLogAdmin(ModelView, model=NotificationLog):
    column_list = [
        NotificationLog.id, NotificationLog.subscription_id, NotificationLog.email,
        NotificationLog.subject, NotificationLog.status, NotificationLog.sent_at,
    ]
    column_searchable_list = [NotificationLog.email, NotificationLog.subject]
    column_sortable_list = [NotificationLog.email, NotificationLog.status, NotificationLog.sent_at]
    column_default_sort = ("sent_at", True)
    page_size = 50
    name = "Notification Log"
    name_plural = "Notification Logs"
    icon = "fa-solid fa-paper-plane"


def setup_admin(app, engine) -> Admin:
    """Create and mount SQLAdmin on the FastAPI app."""
    admin = Admin(
        app,
        engine,
        title="Travel-AI Admin",
        base_url="/admin",
    )
    admin.add_view(UserAdmin)
    admin.add_view(UserPreferenceAdmin)
    admin.add_view(TripAdmin)
    admin.add_view(FlightAdmin)
    admin.add_view(HotelAdmin)
    admin.add_view(ActivityAdmin)
    admin.add_view(ItineraryAdmin)
    admin.add_view(ChatSessionAdmin)
    admin.add_view(PriceHistoryAdmin)
    admin.add_view(SubscriptionAdmin)
    admin.add_view(SubscriptionEmailAdmin)
    admin.add_view(NotificationLogAdmin)
    return admin
