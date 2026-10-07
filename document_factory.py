from abc import ABC, abstractmethod


class Document(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


class Report(Document):
    def render(self) -> str:
        return "Звіт: відображення даних звіту"


class Invoice(Document):
    def render(self) -> str:
        return "Рахунок: відображення даних рахунку"


class Contract(Document):
    def render(self) -> str:
        return "Контракт: відображення даних контракту"


class NullDocument(Document):
    def render(self) -> str:
        return "Документ невідомого типу"


class DocumentFactory:
    @staticmethod
    def create(doc_type: str) -> Document:
        documents = {
            "report": Report,
            "invoice": Invoice,
            "contract": Contract
        }

        document_class = documents.get(doc_type.lower())

        if document_class is None:
            return NullDocument()

        return document_class()


# Клієнтський код
doc_type = input(
    "Введіть тип документа (report/invoice/contract): "
)

document = DocumentFactory.create(doc_type)

print(document.render())