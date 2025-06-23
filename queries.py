from database import Base, get_db

tables = Base.classes.keys()
"""
['merchant_account', 'gateway_status_map', 'blocklist_lookup', 'business_profile', 'dynamic_routing_stats', 'relay', 'refund', 'locker_mock_up', 'reverse_lookup', '__diesel_schema_migrations', 'merchant_key_store', 'user_key_store', 'events', 'process_tracker', 'payouts', 'authentication', 'user_authentication_methods', 'address', 'organization', 'payment_link', 'roles', 'unified_translations', 'dispute', 'merchant_connector_account', 'payment_attempt', 'configs', 'api_keys', 'generic_link', 'blocklist', 'blocklist_fingerprint', 'themes', 'payout_attempt', 'fraud_check', 'user_roles', 'users', 'dashboard_metadata', 'callback_mapper', 'routing_algorithm', 'incremental_authorization', 'captures', 'payment_methods', 'cards_info', 'mandate', 'payment_intent', 'customers', 'file_metadata']
"""
Payments = Base.classes.payment_attempt

db_gen = get_db()
db = next(db_gen)

payments = db.query(Base.classes.merchant_account).all()
merchants = db.query(Base.classes.merchant_account).all()
