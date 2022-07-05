def orm_row_to_dict(object_) -> dict:
    object_ = object_[0]
    to_return = dict()
    for column in object_.__table__.columns:
        to_return[column.name] = getattr(object_, column.name)
    return to_return
