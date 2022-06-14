from sqlalchemy import delete, exists, insert, update
from sqlalchemy.orm import Session


def is_object_exists(session: Session, statement):
    statement = exists(statement).select()
    result = session.execute(statement)
    is_object_exists = result.scalar()
    return is_object_exists


def update_model_instance(session: Session, object_, to_update: dict):
    for column_name, column_value in to_update.items():
        if not hasattr(object_, column_name):
            raise AttributeError(f"The object has no column {column_name}")
        setattr(object_, column_name, column_value)
    session.add(object_)
    session.commit()


def update_object(session: Session, model, where_statements: list, to_update: dict, returning: list):
    statement = update(model).where(*where_statements).values(**to_update).returning(*returning)
    result = session.execute(statement)
    session.commit()
    if returning:
        object_ = result.scalar()
        return object_
    return None


def insert_object(session: Session, model, to_insert: dict, returning: list):
    statement = insert(model).values(**to_insert).returning(*returning)
    result = session.execute(statement)
    session.commit()
    if returning:
        object_ = result.scalar()
        return object_
    return None


def delete_object(session: Session, model, where_statements: list, returning: list=[]):
    statement = delete(model).where(*where_statements).returning(*returning)
    result = session.execute(statement)
    session.commit()
    if returning:
        object_ = result.scalar()
        return object_
    return None


def get_object(session: Session, statement):
    result = session.execute(statement)
    object_ = result.scalar()
    return object_
