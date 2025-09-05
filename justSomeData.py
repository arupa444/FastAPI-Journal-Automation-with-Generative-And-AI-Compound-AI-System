    <div class="col-md-2">
        <label class="form-label">Received</label>
        <input type="date" name="received" class="form-control" required>
    </div>



def add_business_days(start_date: datetime.date, days: int) -> datetime.date:
    current_date = start_date
    added_days = 0
    while added_days < days:
        current_date += datetime.timedelta(days=1)
        if current_date.weekday() < 5:  # Monday=0, Sunday=6
            added_days += 1
    return current_date


def format_date(date_obj: datetime.date) -> str:
    return date_obj.strftime("%d-%b-%Y")



    editorAssigned: Optional[str] = None
    reviewed: Optional[str] = None
    revised: Optional[str] = None
    published: Optional[str] = None

    # Auto-populate extra dates after model init
    def model_post_init(self, __context):
        received_date = datetime.datetime.strptime(self.received, "%Y-%m-%d").date()
        self.editorAssigned = format_date(add_business_days(received_date, 2))
        self.reviewed = format_date(add_business_days(received_date, 2 + 14))
        self.revised = format_date(add_business_days(received_date, 2 + 14 + 7))
        self.published = format_date(add_business_days(received_date, 2 + 14 + 7 + 7))
        self.received = format_date(received_date)






