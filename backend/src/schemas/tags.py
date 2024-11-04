import re

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, field_validator

from backend.src.constants import PARAMS_MAX_LENGTH


class BaseTag(BaseModel):
    name: str = Field(max_length=PARAMS_MAX_LENGTH)
    color: str = Field(max_length=7)
    slug: str = Field(max_length=PARAMS_MAX_LENGTH)


class TagCreate(BaseTag):

    class Config:
        schema_extra = {
            'examples': {
                'Breakfast': {
                    'summary': 'Завтрак',
                    'value': {
                        'name': 'Завтрак',
                        'color': '#f5945c',
                        'slug': 'breakfast'
                    }
                },
                'Lunch': {
                    'summary': 'Обед',
                    'value': {
                        'name': 'Обед',
                        'color': '#75ba75',
                        'slug': 'lunch'
                    }
                },
                'Dinner': {
                    'summary': 'Ужин',
                    'value': {
                        'name': 'Ужин',
                        'color': '#be95be',
                        'slug': 'dinner'
                    }
                }
            }
        }

    @field_validator('slug')
    def validate_slug(cls, value):
        slug_pattern = r'^[-a-zA-Z0-9_]+$'
        if not re.fullmatch(pattern=slug_pattern, string=value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    'Значение поля slug должно соответсвовать '
                    f'паттерну {slug_pattern}'
                )
            )
        return value

    @field_validator('color')
    def validate_color(cls, value):
        color_pattern = r'^#\w{3,6}$'
        if not re.fullmatch(pattern=color_pattern, string=value):

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    'Значение поля color должно соответсвовать '
                    f'паттерну {color_pattern}')
            )
        return value


class TagRead(BaseTag):
    id: int
