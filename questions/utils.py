MIN_CHOICES = 4
MAX_CHOICES = 5


def has_valid_number_of_choices(choices):
    return len(choices) == MIN_CHOICES or len(choices) == MAX_CHOICES


def has_only_one_correct_choice(choices):
    total_true_questions = sum(choice['is_correct'] for choice in choices)
    return total_true_questions == 1


def has_unique_display_order(choices):
    display_order_values = [choice['display_order'] for choice in choices]
    return len(display_order_values) == len(set(display_order_values))
