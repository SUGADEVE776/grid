from djchoices import ChoiceItem, DjangoChoices


class UserTypeChoices(DjangoChoices):
    """Choices for User Type"""

    recruiter = ChoiceItem("recruiter", "Recruiter")
    job_seeker = ChoiceItem("job_seeker", "Job Seeker")


class GenderChoices(DjangoChoices):
    """Choices for Gender"""

    male = ChoiceItem("male", "Male")
    female = ChoiceItem("female", "Female")
    transgender = ChoiceItem("transgender", "Transgender")
