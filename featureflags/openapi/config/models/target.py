from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.segment import Segment
    from ..models.target_attributes import TargetAttributes


T = TypeVar("T", bound="Target")


@_attrs_define
class Target:
    """A Target object

    Attributes:
        identifier (str): The unique identifier for this target Example: john-doe.
        account (str): The account ID that the target belongs to Example: abcXDdffdaffd.
        org (str): The identifier for the organization that the target belongs to
        environment (str): The identifier for the environment that the target belongs to
        project (str): The identifier for the project that this target belongs to
        name (str): The name of this Target Example: John Doe.
        anonymous (Union[Unset, bool]): Indicates if this target is anonymous
        attributes (Union[Unset, TargetAttributes]): a JSON representation of the attributes for this target Example:
            {'age': 20, 'location': 'Belfast'}.
        created_at (Union[Unset, int]): The date and time in milliseconds when this Target was created
        segments (Union[Unset, List['Segment']]): A list of Target Groups (Segments) that this Target belongs to
    """

    identifier: str
    account: str
    org: str
    environment: str
    project: str
    name: str
    anonymous: Union[Unset, bool] = UNSET
    attributes: Union[Unset, "TargetAttributes"] = UNSET
    created_at: Union[Unset, int] = UNSET
    segments: Union[Unset, List["Segment"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier

        account = self.account

        org = self.org

        environment = self.environment

        project = self.project

        name = self.name

        anonymous = self.anonymous

        attributes: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        created_at = self.created_at

        segments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.segments, Unset):
            segments = []
            for segments_item_data in self.segments:
                segments_item = segments_item_data.to_dict()
                segments.append(segments_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "account": account,
                "org": org,
                "environment": environment,
                "project": project,
                "name": name,
            }
        )
        if anonymous is not UNSET:
            field_dict["anonymous"] = anonymous
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if segments is not UNSET:
            field_dict["segments"] = segments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.segment import Segment
        from ..models.target_attributes import TargetAttributes

        d = src_dict.copy()
        identifier = d.pop("identifier")

        account = d.pop("account")

        org = d.pop("org")

        environment = d.pop("environment")

        project = d.pop("project")

        name = d.pop("name")

        anonymous = d.pop("anonymous", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, TargetAttributes]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = TargetAttributes.from_dict(_attributes)

        created_at = d.pop("createdAt", UNSET)

        segments = []
        _segments = d.pop("segments", UNSET)
        for segments_item_data in _segments or []:
            segments_item = Segment.from_dict(segments_item_data)

            segments.append(segments_item)

        target = cls(
            identifier=identifier,
            account=account,
            org=org,
            environment=environment,
            project=project,
            name=name,
            anonymous=anonymous,
            attributes=attributes,
            created_at=created_at,
            segments=segments,
        )

        target.additional_properties = d
        return target

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
