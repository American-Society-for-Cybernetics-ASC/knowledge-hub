from database.model import Member


def test_member_fields_exist():
    member = Member(member_id=1, status="active", group_id=10)

    assert member.member_id == 1
    assert member.status == "active"
    assert member.group_id == 10
