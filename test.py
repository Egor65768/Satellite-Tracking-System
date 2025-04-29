from app.schemas import CountryCreate

c = CountryCreate(
    abbreviation="CA",
    full_name="Canada"
)

print(type(c.model_dump()))

