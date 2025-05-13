from __future__ import annotations

from collections.abc import Iterable, Mapping
import io
import mimetypes
import pathlib
import typing
from typing import Any, TypedDict, Union

from google.ai import generativelanguage as glm

if typing.TYPE_CHECKING:
    import PIL.Image
    import IPython.display

    IMAGE_TYPES = (PIL.Image.Image, IPython.display.Image)
else:
    IMAGE_TYPES = ()
    try:
        import PIL.Image

        IMAGE_TYPES = IMAGE_TYPES + (PIL.Image.Image,)
    except ImportError:
        PIL = None

    try:
        import IPython.display

        IMAGE_TYPES = IMAGE_TYPES + (IPython.display.Image,)
    except ImportError:
        IPython = None


__all__ = [
    "BlobDict",
    "BlobType",
    "PartDict",
    "PartType",
    "ContentDict",
    "ContentType",
    "StrictContentType",
    "ContentsType",
]


def pil_to_blob(img):
    bytesio = io.BytesIO()
    if isinstance(img, PIL.PngImagePlugin.PngImageFile):
        img.save(bytesio, format="PNG")
        mime_type = "image/png"
    else:
        img.save(bytesio, format="JPEG")
        mime_type = "image/jpeg"
    bytesio.seek(0)
    data = bytesio.read()
    return glm.Blob(mime_type=mime_type, data=data)


def image_to_blob(image) -> glm.Blob:
    if PIL is not None:
        if isinstance(image, PIL.Image.Image):
            return pil_to_blob(image)

    if IPython is not None:
        if isinstance(image, IPython.display.Image):
            name = image.filename
            if name is None:
                raise ValueError(
                    "Can only convert `IPython.display.Image` if "
                    "it is constructed from a local file (Image(filename=...))."
                )

            mime_type, _ = mimetypes.guess_type(name)
            if mime_type is None:
                mime_type = "image/unknown"

            return glm.Blob(mime_type=mime_type, data=image.data)

    raise TypeError(
        "Could not convert image. expected an `Image` type"
        "(`PIL.Image.Image` or `IPython.display.Image`).\n"
        f"Got a: {type(image)}\n"
        f"Value: {image}"
    )


class BlobDict(TypedDict):
    mime_type: str
    data: bytes


def _convert_dict(d: Mapping) -> glm.Content | glm.Part | glm.Blob:
    if is_content_dict(d):
        content = dict(d)
        content["parts"] = [to_part(part) for part in content["parts"]]
        return glm.Content(content)
    elif is_part_dict(d):
        part = dict(d)
        if "inline_data" in part:
            part["inline_data"] = to_blob(part["inline_data"])
        return glm.Part(part)
    elif is_blob_dict(d):
        blob = d
        return glm.Blob(blob)
    else:
        raise KeyError(
            "Could not recognize the intended type of the `dict`. "
            "A `Content` should have a 'parts' key. "
            "A `Part` should have a 'inline_data' or a 'text' key. "
            "A `Blob` should have 'mime_type' and 'data' keys. "
            f"Got keys: {list(d.keys())}"
        )


def is_blob_dict(d):
    return "mime_type" in d and "data" in d


if typing.TYPE_CHECKING:
    BlobType = Union[
        glm.Blob, BlobDict, PIL.Image.Image, IPython.display.Image
    ]  # Any for the images
else:
    BlobType = Union[glm.Blob, BlobDict, Any]


def to_blob(blob: BlobType) -> glm.Blob:
    if isinstance(blob, Mapping):
        blob = _convert_dict(blob)

    if isinstance(blob, glm.Blob):
        return blob
    elif isinstance(blob, IMAGE_TYPES):
        return image_to_blob(blob)
    else:
        if isinstance(blob, Mapping):
            raise KeyError(
                "Could not recognize the intended type of the `dict`\n" "A content should have "
            )
        raise TypeError(
            "Could not create `Blob`, expected `Blob`, `dict` or an `Image` type"
            "(`PIL.Image.Image` or `IPython.display.Image`).\n"
            f"Got a: {type(blob)}\n"
            f"Value: {blob}"
        )


class PartDict(TypedDict):
    text: str
    inline_data: BlobType


# When you need a `Part` accept a part object, part-dict, blob or string
PartType = Union[glm.Part, PartDict, BlobType, str]


def is_part_dict(d):
    return "text" in d or "inline_data" in d


def to_part(part: PartType):
    if isinstance(part, Mapping):
        part = _convert_dict(part)

    if isinstance(part, glm.Part):
        return part
    elif isinstance(part, str):
        return glm.Part(text=part)
    else:
        # Maybe it can be turned into a blob?
        return glm.Part(inline_data=to_blob(part))


class ContentDict(TypedDict):
    parts: list[PartType]
    role: str


def is_content_dict(d):
    return "parts" in d


# When you need a message accept a `Content` object or dict, a list of parts,
# or a single part
ContentType = Union[glm.Content, ContentDict, Iterable[PartType], PartType]

# For generate_content, we're not guessing roles for [[parts],[parts],[parts]] yet.
StrictContentType = Union[glm.Content, ContentDict]


def to_content(content: ContentType):
    if isinstance(content, Mapping):
        content = _convert_dict(content)

    if isinstance(content, glm.Content):
        return content
    elif isinstance(content, Iterable) and not isinstance(content, str):
        return glm.Content(parts=[to_part(part) for part in content])
    else:
        # Maybe this is a Part?
        return glm.Content(parts=[to_part(content)])


def strict_to_content(content: StrictContentType):
    if isinstance(content, Mapping):
        content = _convert_dict(content)

    if isinstance(content, glm.Content):
        return content
    else:
        raise TypeError(
            "Expected a `glm.Content` or a `dict(parts=...)`.\n"
            f"Got type: {type(content)}\n"
            f"Value: {content}\n"
        )


ContentsType = Union[ContentType, Iterable[StrictContentType], None]


def to_contents(contents: ContentsType) -> list[glm.Content]:
    if contents is None:
        return []

    if isinstance(contents, Iterable) and not isinstance(contents, (str, Mapping)):
        try:
            # strict_to_content so [[parts], [parts]] doesn't assume roles.
            contents = [strict_to_content(c) for c in contents]
            return contents
        except TypeError:
            # If you get a TypeError here it's probably because that was a list
            # of parts, not a list of contents, so fall back to `to_content`.
            pass

    contents = [to_content(contents)]
    return contents
