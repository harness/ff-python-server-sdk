from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evaluation import Evaluation


T = TypeVar("T", bound="GetEvaluationsResponse200")


@_attrs_define
class GetEvaluationsResponse200:
    """
    Attributes:
        page_count (int): The total number of pages Example: 100.
        item_count (int): The total number of items Example: 1.
        page_size (int): The number of items per page Example: 1.
        page_index (int): The current page
        version (Union[Unset, int]): The version of this object.  The version will be incremented each time the object
            is modified Example: 5.
        evaluations (Union[Unset, List['Evaluation']]):
    """

    page_count: int
    item_count: int
    page_size: int
    page_index: int
    version: Union[Unset, int] = UNSET
    evaluations: Union[Unset, List["Evaluation"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        page_count = self.page_count

        item_count = self.item_count

        page_size = self.page_size

        page_index = self.page_index

        version = self.version

        evaluations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.evaluations, Unset):
            evaluations = []
            for componentsschemas_evaluations_item_data in self.evaluations:
                componentsschemas_evaluations_item = (
                    componentsschemas_evaluations_item_data.to_dict()
                )
                evaluations.append(componentsschemas_evaluations_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pageCount": page_count,
                "itemCount": item_count,
                "pageSize": page_size,
                "pageIndex": page_index,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version
        if evaluations is not UNSET:
            field_dict["evaluations"] = evaluations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.evaluation import Evaluation

        d = src_dict.copy()
        page_count = d.pop("pageCount")

        item_count = d.pop("itemCount")

        page_size = d.pop("pageSize")

        page_index = d.pop("pageIndex")

        version = d.pop("version", UNSET)

        evaluations = []
        _evaluations = d.pop("evaluations", UNSET)
        for componentsschemas_evaluations_item_data in _evaluations or []:
            componentsschemas_evaluations_item = Evaluation.from_dict(
                componentsschemas_evaluations_item_data
            )

            evaluations.append(componentsschemas_evaluations_item)

        get_evaluations_response_200 = cls(
            page_count=page_count,
            item_count=item_count,
            page_size=page_size,
            page_index=page_index,
            version=version,
            evaluations=evaluations,
        )

        get_evaluations_response_200.additional_properties = d
        return get_evaluations_response_200

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
