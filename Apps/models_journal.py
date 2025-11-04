"""
This module defines data models and utility classes for journal generation and management.
Classes:
    GeminiRequest: Model for Gemini prompt requests.
    GroqRequest: Model for Groq prompt requests.
    CoreRequest: Model for Core prompt requests.
    LatexRequest: Model for LaTeX source requests.
    DateUtils: Utility class for date formatting and business day calculations.
    PulsusInputStr: Model for input journal data, including validation and computed fields.
    UpdateInputPartJournal: Model for updating parts of a journal input.
    TranslatePage: Model for page translation requests.
    ArticleItem: Model representing an article item with metadata.
    PulsusOutputStr: Model for output journal data, including validation and computed fields.
Functions and Methods:
    DateUtils.add_business_days(start_date, days, brand): Adds business days or calendar days based on brand.
    DateUtils.format_date(date_obj): Formats a date object to 'DD-Mon-YYYY'.
    PulsusInputStr.model_post_init(__context): Populates extra date fields after model initialization.
    PulsusInputStr.validatePDFNo(value): Validates uniqueness of pdfNo.
    PulsusInputStr.citeAuthorFormate: Returns citation format based on brand.
    PulsusOutputStr.validatePDFNo(value): Validates content dictionary for required fields.
    PulsusOutputStr.copyrightAuthor: Computes copyright author string.
    PulsusOutputStr.addressForCorres: Computes address for correspondence.
    PulsusOutputStr.citation: Computes citation string based on brand.
Imports:
    Various types and utilities from local modules for model definition and validation.

"""

from Apps.library_import import (
    BaseModel,
    Field,
    EmailStr,
    AnyUrl,
    Annotated,
    Optional,
    List,
    Dict,
    BaseModel,
    Field,
    field_validator,
    computed_field,
    datetime,
)
from Apps.services.io_service import IOService


class GeminiRequest(BaseModel):
    prompt: str = Field(
        ...,
        title="Here, we can use Gemini",
        description="Enter prompt for the Gemini to compute....",
    )


class GroqRequest(BaseModel):
    prompt: str = Field(
        ...,
        title="Here, we can use Groq",
        description="Enter prompt for the Groq to compute....",
    )


class CoreRequest(BaseModel):
    prompt: str = Field(
        ...,
        title="Here, we can use Core for Research pages",
        description="Enter prompt for the Core to compute....",
    )


class LatexRequest(BaseModel):
    source: str


class DateUtils:
    """Utility methods for date formatting and business day calculation."""

    @staticmethod
    def add_business_days(
        start_date: datetime.date, days: int, brand: str
    ) -> datetime.date:
        """Add business days (or calendar days for hilaris)."""
        current_date = start_date

        if brand == "alliedAcademy.tex":
           # Count only weekdays
            added_days = 0
            while added_days < days:
                current_date += datetime.timedelta(days=1)
                if current_date.weekday() < 5:
                    added_days += 1
        else:
             # Just add calendar days
            current_date += datetime.timedelta(days=days)
            # If it lands on Saturday/Sunday, move to Monday
            while current_date.weekday() > 4:
                current_date += datetime.timedelta(days=1)
        return current_date

    @staticmethod
    def format_date(date_obj: datetime.date) -> str:
        """Return date in `DD-Mon-YYYY` format."""
        return date_obj.strftime("%d-%b-%Y")


class PulsusInputStr(BaseModel):
    id: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
            max_length=6,
            min_length=3,
        ),
    ]
    topic: Annotated[
        str, Field(..., title="Name of the topic", description="Enter the topic....")
    ]
    journalName: Annotated[
        str,
        Field(
            ...,
            title="Name of the journal where it belongs to.",
            description="Enter the journal where it belongs from...",
        ),
    ]
    shortJournalName: Annotated[
        str,
        Field(
            ...,
            title="Name of the short journal name where it belongs to.",
            description="Enter the short journal name where it belongs from...",
        ),
    ]
    type: Annotated[
        str,
        Field(
            ...,
            title="Name of the type(journal)",
            description="Enter the type of journal....",
        ),
    ]
    author: Annotated[
        str, Field(..., title="Name of the author", description="Enter the author....")
    ]
    email: Annotated[
        EmailStr,
        Field(
            ..., title="Email of the author", description="Enter the autors email...."
        ),
    ]
    brandName: Annotated[
        str,
        Field(
            ...,
            title="Name of the brand",
            description="Enter the name of your brand...",
        ),
    ]
    authorsDepartment: Annotated[
        str,
        Field(
            ...,
            title="Department of the authour",
            description="Enter the department of the author....",
        ),
    ]
    received: Annotated[
        str,
        Field(
            ...,
            title="The receiving date",
            description="Enter the receiving date in DD-Mon format....",
        ),
    ]
    manuscriptNo: Annotated[
        str,
        Field(
            ...,
            title="The manuscriptNo of this journal",
            description="Enter the manuscriptNo for this journal....",
        ),
    ]
    volume: Annotated[
        int,
        Field(
            ...,
            title="The volume for the issue",
            description="Enter the Volume of the issue...",
            gt=0,
        ),
    ]
    issues: Annotated[
        int,
        Field(
            ...,
            title="The issue no. of the volume",
            description="Enter the issue no. of the volume...",
            gt=0,
        ),
    ]
    pdfNo: Annotated[
        int,
        Field(
            ..., title="The pdf number", description="Enter the pdf number....", gt=0
        ),
    ]
    doi: Annotated[
        Optional[str],
        Field(
            default="",
            title="DOI for this journal",
            description="Enter DOI for this Journal....",
        ),
    ]
    ISSN: Annotated[
        Optional[str],
        Field(
            default=None,
            title="ISSN number of this journal",
            description="Enter the ISSN number for the journal....",
        ),
    ]
    imgPath: Annotated[
        Optional[str],
        Field(default=None, title="image path", description="Enter the img path...."),
    ]
    parentLink: Annotated[
        AnyUrl,
        Field(
            ...,
            title="The url for the centralized link",
            description="Enter the link which will led to the centralized page....",
        ),
    ]

    editorAssigned: Optional[str] = None
    reviewed: Optional[str] = None
    revised: Optional[str] = None
    published: Optional[str] = None

    # Auto-populate extra dates after model init
    def model_post_init(self, __context):
        tempDate = []
        if self.brandName == "alliedAcademy.tex":
            tempDate = [2, 14, 7, 7]
        else:
            tempDate = [2, 14, 5, 7]
        received_date = datetime.datetime.strptime(self.received, "%Y-%m-%d").date()
        self.editorAssigned = DateUtils.format_date(
            DateUtils.add_business_days(received_date, tempDate[0], self.brandName)
        )
        self.reviewed = DateUtils.format_date(
            DateUtils.add_business_days(
                received_date, tempDate[0] + tempDate[1], self.brandName
            )
        )
        self.revised = DateUtils.format_date(
            DateUtils.add_business_days(
                received_date, tempDate[0] + tempDate[1] + tempDate[2], self.brandName
            )
        )
        self.published = DateUtils.format_date(
            DateUtils.add_business_days(
                received_date,
                tempDate[0] + tempDate[1] + tempDate[2] + tempDate[3],
                self.brandName,
            )
        )
        self.received = DateUtils.format_date(received_date)

    
    @computed_field
    @property
    def citeAuthorFormate(self) -> str:
        if self.brandName == "hilaris.tex":
            return """author full names(there must be 3 to 6 authors and seperated with comma). title of that journal inside double quotation(“ ”). Journal short name Volume of the journal (year of publishing inside parenthesis):the page range or the number.end it with a full stop (for example: 'first author full name, second author full name, third author full name. “titleOFtheJournal.” journalShortName Volume (year):ThePageRangeOrTheNumber.')"""

        elif self.brandName == "alliedAcademy.tex":
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 or less, not more authors then that and seperated with comma). title of that journal. Journal short name. year of publishing;Volume of the journal:the page range or the number.(for example: 'author n, author n, author n. titleOFtheJournal. journalShortName. year;Volume:ThePageRangeOrTheNumber.')"""

        elif self.brandName == "omics.tex":
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 to 6 authors and seperated with comma) (year of publishing inside parenthesis) title of that journal. Journal short name Volume of the journal:the page range or the number.(for example: 'author n, author n, author n (year) titleOFtheJournal. journalShortName Volume:ThePageRangeOrTheNumber')"""

        else:
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 or less, not more authors then that and seperated with comma). title of that journal. Journal short name. year of publishing;Volume of the journal:the page range or the number.(for example: 'author n, author n, author n. titleOFtheJournal. journalShortName. year;Volume:ThePageRangeOrTheNumber.')"""
    @field_validator("author")
    @classmethod
    def validateAuthor(cls, value):
        if len(value.split(" "))>1:
            return value
        else:
            raise ValueError({"Message":"Author name must contain at least first name and last name."})


class UpdateInputPartJournal(BaseModel):
    id: Annotated[
        Optional[str],
        Field(
            default=None,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    topic: Annotated[
        Optional[str],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]
    journalName: Annotated[
        Optional[str],
        Field(
            default=None,
            title="Name of the journal where it belongs to.",
            description="Enter the journal where it belongs from...",
        ),
    ]
    shortJournalName: Annotated[
        Optional[str],
        Field(
            default=None,
            title="Name of the short journal name where it belongs to.",
            description="Enter the short journal name where it belongs from...",
        ),
    ]
    type: Annotated[
        Optional[str],
        Field(
            default=None,
            title="Name of the type(journal)",
            description="Enter the type of journal....",
        ),
    ]
    author: Annotated[
        Optional[str],
        Field(
            default=None, title="Name of the author", description="Enter the author...."
        ),
    ]
    email: Annotated[
        Optional[EmailStr],
        Field(
            default=None,
            title="Email of the author",
            description="Enter the autors email....",
        ),
    ]
    brandName: Annotated[
        Optional[str],
        Field(
            default=None,
            title="Name of the brand",
            description="Enter the name of your brand...",
        ),
    ]
    authorsDepartment: Annotated[
        Optional[str],
        Field(
            default=None,
            title="Department of the authour",
            description="Enter the department of the author....",
        ),
    ]
    received: Annotated[
        Optional[str],
        Field(
            default=None,
            title="The receiving date",
            description="Enter the receiving date in DD-Mon format....",
        ),
    ]
    editorAssigned: Annotated[
        Optional[str],
        Field(
            default=None,
            title="The Editor Assigned date",
            description="Enter the editor assigned date in DD-Mon format....",
        ),
    ]
    reviewed: Annotated[
        Optional[str],
        Field(
            default=None,
            title="The journal review date",
            description="Enter the journal review date in DD-Mon format....",
        ),
    ]
    revised: Annotated[
        Optional[str],
        Field(
            default=None,
            title="The journal revised date",
            description="Enter the journal revised date in DD-Mon format....",
        ),
    ]
    published: Annotated[
        Optional[str],
        Field(
            default=None,
            title="The publishing date of journal",
            description="Enter the publishing date of the journal in DD-Mon format....",
        ),
    ]
    manuscriptNo: Annotated[
        Optional[str],
        Field(
            default=None,
            title="The manuscriptNo of this journal",
            description="Enter the manuscriptNo for this journal....",
        ),
    ]
    volume: Annotated[
        Optional[int],
        Field(
            default=None,
            title="The volume for the issue",
            description="Enter the Volume of the issue...",
            gt=0,
        ),
    ]
    issues: Annotated[
        Optional[int],
        Field(
            default=None,
            title="The issue no. of the volume",
            description="Enter the issue no. of the volume...",
            gt=0,
        ),
    ]
    pdfNo: Annotated[
        Optional[int],
        Field(
            default=None,
            title="The pdf number",
            description="Enter the pdf number....",
            gt=0,
        ),
    ]
    doi: Annotated[
        Optional[str],
        Field(
            default=None,
            title="DOI for this journal",
            description="Enter DOI for this Journal....",
        ),
    ]
    ISSN: Annotated[
        Optional[str],
        Field(
            default=None,
            title="ISSN number of this journal",
            description="Enter the ISSN number for the journal....",
        ),
    ]
    imgPath: Annotated[
        Optional[str],
        Field(default=None, title="image path", description="Enter the img path...."),
    ]
    parentLink: Annotated[
        Optional[AnyUrl],
        Field(
            default=None,
            title="The url for the centralized link",
            description="Enter the link which will led to the centralized page....",
        ),
    ]


class TranslatePage(BaseModel):
    id: Annotated[
        str,
        Field(
            ...,
            title="The id of the page",
            description="Enter the id of the page....",
            min_length=3,
            max_length=6,
        ),
    ]
    language: Annotated[
        str,
        Field(
            default=None,
            title="The language of the page",
            description="Enter the language of the page....",
        ),
    ]


class ArticleItem(BaseModel):
    title: Annotated[
        Optional[str],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]
    subContent: Annotated[
        Optional[str],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]
    authors: Annotated[
        Optional[str],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]
    published: Annotated[
        Optional[str],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]
    doi: Annotated[
        Optional[str],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]
    url: Annotated[
        Optional[AnyUrl],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]
    fulltextLinks: Annotated[
        Optional[List[str]],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]
    keywords: Annotated[
        Optional[str],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]
    references: Annotated[
        Optional[str],
        Field(
            default=None, title="Name of the topic", description="Enter the topic...."
        ),
    ]


class PulsusOutputStr(BaseModel):
    title: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    journalName: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    shortJournalName: Annotated[
        str,
        Field(
            ...,
            title="Name of the short journal name where it belongs to.",
            description="Enter the short journal name where it belongs from...",
        ),
    ]
    type: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    author: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    email: Annotated[
        EmailStr,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    brandName: Annotated[
        str,
        Field(
            ...,
            title="Name of the brand",
            description="Enter the name of your brand...",
        ),
    ]
    authorsDepartment: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    journalYearVolumeIssue: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    introduction: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    description: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    content: Annotated[
        Dict[str, Dict],
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    abstract: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    keywords: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    doi: Annotated[
        Optional[str],
        Field(
            default=None,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    received: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    editorAssigned: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    reviewed: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    revised: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    published: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    year: Annotated[
        int,
        Field(
            ...,
            title="Yes of publishing",
            description="Enter the journal publising year...",
        ),
    ]
    manuscriptNo: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    QCNo: Annotated[
        str, Field(..., title="The QC number", description="Enter the QC number....")
    ]
    preQCNo: Annotated[
        str,
        Field(..., title="The preQC number", description="Enter the preQC number...."),
    ]
    RManuNo: Annotated[
        str,
        Field(
            ..., title="The RManuNo number", description="Enter the RManuNo number...."
        ),
    ]
    volume: Annotated[
        str,
        Field(
            ...,
            title="The volume for the issue",
            description="Enter the Volume of the issue...",
        ),
    ]
    issues: Annotated[
        str,
        Field(
            ...,
            title="The issue no. of the volume",
            description="Enter the issue no. of the volume...",
        ),
    ]
    ISSN: Annotated[
        Optional[str],
        Field(default="", title="ISSN Number", description="Enter the ISSN Number...."),
    ]
    imgPath: Annotated[
        Optional[str],
        Field(default=None, title="image path", description="Enter the img path...."),
    ]
    pdfNo: Annotated[
        int, Field(..., title="Pdf Number", description="Enter the PDF Number....")
    ]
    parentLink: Annotated[
        AnyUrl,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    conclusion: Annotated[
        str,
        Field(
            ...,
            title="ID of the Input Journal",
            description="Enter the id for this journal input....",
        ),
    ]
    @computed_field
    @property
    def firstNameAuthor(self) -> str:
        copyAuth = self.author.split(' ')
        return copyAuth[0]

    @field_validator("content")
    @classmethod
    def validatePDFNo(cls, value):
        # Avoid modifying dict during iteration
        keys_to_delete = []
        for i, j in value.items():
            if j.get("subContent") is None or j.get("references") is None:
                keys_to_delete.append(i)
        for k in keys_to_delete:
            del value[k]
        return value

    @computed_field
    @property
    def copyrightAuthor(self) -> str:
        copyAuth = self.author.split(" ")
        copyAuth = copyAuth[::-1]
        copyAuth[1] = f"{copyAuth[1][0]}."
        return " ".join(copyAuth)

    @computed_field
    @property
    def addressForCorres(self) -> str:
        copyAuth = self.author.split(" ")
        copyAuth[0] = f"{copyAuth[0]},"
        return " ".join(copyAuth)

    @computed_field
    @property
    def citation(self) -> str:
        if self.brandName == "hilaris.tex":
            justToCite = self.author.split(" ")
            justToCite = f"{justToCite[-1]}{" ".join(justToCite[:-1])}"
            return f"""{justToCite}. "{self.title}." {self.shortJournalName} {self.volume} ({self.published.split("-")[-1]}):{self.pdfNo}."""

        elif self.brandName == "alliedAcademy.tex":
            justToCite = self.author.split(" ")
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            for i in range(1, len(justToCite)):
                justToCite[i] = justToCite[i][0]
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"""{justToCite}. {self.title}. {self.shortJournalName}. {self.published.split("-")[-1]};{self.volume}({self.issues}):{self.pdfNo}."""

        elif self.brandName == 'omics.tex':
            justToCite = self.author.split(' ')
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            for i in range(1, len(justToCite)):
                justToCite[i] = justToCite[i][0]
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"""{justToCite} ({self.published.split("-")[-1]}) {self.title}. {self.shortJournalName} {self.volume}: {self.pdfNo}."""
        
        else:
            justToCite = self.author.split(" ")
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            for i in range(1, len(justToCite)):
                justToCite[i] = justToCite[i][0]
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"""{justToCite},({self.published.split("-")[-1]}) {self.title}. {self.shortJournalName} {self.volume}: {self.pdfNo}. DOI: {self.doi}"""
