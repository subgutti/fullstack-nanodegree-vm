from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Add dummy user
User1 = User(name="Subhash Guttikonda", email="subgutti@gmail.com",
             picture='https://lh6.googleusercontent.com/-xu4mYMJ8J7c/AAAAAAAAAAI/AAAAAAAANDg/_R-09t8IVhE/photo.jpg')
session.add(User1)
session.commit()

# Add Categories and their items

# Soccer
category1 = Category(user_id=1, name="Soccer")
session.add(category1)
session.commit()

item1 = Item(title="Soccer Socks", description="Soccer socks are extremely long. They cover shin-gaurds",
             category=category1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(title="Shin-Gaurds", description="Shin-gaurds protect player's shins, a vulnerable part of player's body that often gets kicked",
             category=category1, user_id=1)
session.add(item2)
session.commit()


item3 = Item(title="Soccer Ball", description="Soccer balls allows players to train and play individually or with friends outside for practise",
             category=category1, user_id=1, image="https://upload.wikimedia.org/wikipedia/en/e/ec/Soccer_ball.svg")
session.add(item3)
session.commit()

# Basketball
category2 = Category(user_id=1, name="Basketball")
session.add(category2)
session.commit()

item4 = Item(title="Basketball Sneakers", description="Players should wear comfortable, properly fitting basketball sneakers.",
             category=category2, user_id=1, image="http://ecx.images-amazon.com/images/I/91%2BXlOzjTwL._UX695_.jpg")
session.add(item4)
session.commit()

item5 = Item(title="Knee Pads", description="Players should wear knee pads to protect themselves during falls or dives to the floor",
             category=category2, user_id=1, image="http://ecx.images-amazon.com/images/I/41j6DLiGSJL.jpg")
session.add(item5)
session.commit()

# Baseball
category3 = Category(user_id=1, name="Baseball")
session.add(category3)
session.commit()

item6 = Item(title="Baseball Glove", description="The quality of baseball gloves varies based mostly on the material (usually leather) that it's made out of. There are some very high end leather gloves on the market that are north of $500! These gloves are used mostly by professional players.",
             category=category3, user_id=1, image="http://ecx.images-amazon.com/images/I/51VqFOSQKXL.jpg")
session.add(item6)
session.commit()

item7 = Item(title="Baseball Bat", description="You can't really play baseball without a bat! While there is a ton of fun to be had by just getting your glove on and playing catch with a friend, the game itself involves hitting and that means a bat.",
             category=category3, user_id=1, image="http://ecx.images-amazon.com/images/I/71hNsLWogPL._SX522_.jpg")
session.add(item7)
session.commit()


# Frisbee
category4 = Category(user_id=1, name="Frisbee")
session.add(category4)
session.commit()

# Snowboarding
category5 = Category(user_id=1, name="Snowboarding")
session.add(category5)
session.commit()

# Rock Climbing
category6 = Category(user_id=1, name="Rock Climbing")
session.add(category6)
session.commit()

print "Populated Catalog!"
