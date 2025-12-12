from database import listings_collection

# Delete listings that don't have a user_id
result = listings_collection.delete_many({"user_id": {"$exists": False}})

print("Deleted:", result.deleted_count, "old listings")
