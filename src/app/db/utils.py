def orm_row_to_dict(object_) -> dict:
    to_return = dict()
    for column in object_[0].__table__.columns:
        to_return[column.name] = getattr(object_[0], column.name)
    return to_return
