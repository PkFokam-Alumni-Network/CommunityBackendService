import uvicorn
from fastapi import FastAPI,HTTPException
from fastapi.params import Body
from pydantic import BaseModel

app = FastAPI()


user_database=[{
    "username": "Evilstar",
    "email": "kiracedric05@yahoo.com",
    "Phone_number": 100000001,
    "linkedin":"https://www.linkedin.com/in/cedric-kouega"
    },
    {
    "username": "Renwarren",
    "email": "bjoelfra@gmail.com",
    "Phone_number": 100000002,
    "linkedin":"https://www.linkedin.com/in/warren-fongang-chendjou"
    
    },
    {"username": "bjoelfra",
    "email": "bjoelfra@gmail.com",
    "Phone_number": 100000003,
    "linkedin":"https://www.linkedin.com/in/bangbang-joel-francois"
     },
     {"username": "harld",
    "email": "harld@gmail.com",
    "Phone_number": 100000004,
    "linkedin":"https://www.linkedin.com/in/yann-djoumessi"
     }
     ,
     {"username": "atakoutene",
    "email": "takoutene@gmail.com",
    "Phone_number": 100000005,
    "linkedin":"https://www.linkedin.com/in/aurelien-takou"
     }
     ]

class Post(BaseModel):
    username: str
    email:str
    Phone_number: int
    linkedin: str

def find_user(username:str):
    for user in user_database:
        print(user["username"])
        if user["username"]==username:
            return user
    
    
    

@app.put("/posts/{username}")
def update_user_info(username:str, post: Post):
    user_cred=find_user(username)
    print(user_cred)
    new_cred=post.model_dump()
    if not user_cred:
         raise HTTPException(status_code=404, detail= f"post with {username} was not found")
    for keyA in user_cred:
        for keyB in new_cred:
            if keyA==keyB:
                user_cred[keyA]=new_cred[keyB]
    index=user_database.index(new_cred)
    user_database[index]= user_cred
    return{ "updated data":user_database[index]}
