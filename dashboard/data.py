import datetime

from trello.trelloclient import TrelloClient


BOARD_ID = '5f7f61eda018ce481185be8f'

COLOR_EPIC = 'purple'
COLOR_TASK = 'blue'
COLOR_PRODUCT = None

LIST_DONE = 'Done'
LIST_IN_PROGRESS = 'In Progress'


class DashboardData:

    def __init__(self):
        self.board = None
        self.all_labels = None  # [Label]
        self.all_cards = None  # [Card]
        self.all_lists = None  # [TrelloList]
        self.all_members = None  # [Member]

        self.label_names = None  # [str]
        self.epic_label_names = None  # [str]
        self.task_label_names = None  # [str]
        self.product_label_names = None  # [str]

        self.members_by_id = {}  # [str: Member]

        self.list_names = None  # [str]
        self.lists_by_id = None  # {str: [List]}
        self.lists_by_name = None  # {str: [List]}
        self.ongoing_list_ids = None  # [str]

        self.cards_by_list_id = {}  # {str: [Card]}
        self.cards_by_label = {}  # {str: [Card]}

    def load(self, client: TrelloClient) -> None:
        """
        Loads all of the necessary data from the Trello client, organizing it as necessary
        for future calls. No other calls should be made to objects of this class without having
        first called this method.

        :param client: authenticated trello client
        """

        # Live network calls
        self.board = client.get_board(BOARD_ID)
        self.all_labels = self.board.get_labels()
        self.all_cards = self.board.all_cards()
        self.all_lists = self.board.all_lists()
        self.all_members = self.board.all_members()

        # Organize labels
        self.label_names = [label.name for label in self.all_labels]

        self.epic_label_names = [label.name for label in self.all_labels if label.color == COLOR_EPIC]
        self.task_label_names = [label.name for label in self.all_labels if label.color == COLOR_TASK]
        self.product_label_names = [label.name for label in self.all_labels if label.color == COLOR_PRODUCT]

        # Organize members
        self.members_by_id = {m.id: m for m in self.all_members}

        # Organize lists
        self.list_names = [tlist.name for tlist in self.all_lists]
        self.lists_by_id = {tlist.id: tlist for tlist in self.all_lists}
        self.lists_by_name = {tlist.name: tlist for tlist in self.all_lists}

        self.ongoing_list_ids = (
            self.lists_by_name[LIST_DONE].id,
            self.lists_by_name[LIST_IN_PROGRESS].id
        )

        # Organize cards
        for card in self.all_cards:
            # Rebuild date as a date object
            if card.due:
                card.real_due_date = datetime.datetime.strptime(card.due, '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                card.real_due_date = None

            # Add in member names instead of IDs
            card.member_names = [self.members_by_id[m_id].full_name for m_id in card.member_ids]

            # Label breakdown
            if card.labels:
                for label in card.labels:
                    mapping = self.cards_by_label.setdefault(label.name, [])
                    mapping.append(card)

            # List breakdown
            self.cards_by_list_id.setdefault(card.list_id, []).append(card)

    def in_progress_cards(self):
        in_progress_id = self.lists_by_name[LIST_IN_PROGRESS].id
        in_progress_cards = self.cards_by_list_id[in_progress_id]

        # Add a new "type" field that describes the type of task represented by
        # the card. Since the knowledge of what a label represents is captured in the
        # color, we do this here and then make the new list available to the UI.
        add_card_types(in_progress_cards, self.task_label_names)

        sorted_cards = sorted(in_progress_cards, key=sort_cards_by_due)
        return sorted_cards

    def done_cards(self):
        done_id = self.lists_by_name[LIST_DONE].id
        done_cards = self.cards_by_list_id[done_id]
        add_card_types(done_cards, self.task_label_names)
        sorted_cards = sorted(done_cards, key=sort_cards_by_due)
        return sorted_cards

    def ongoing_products(self):
        ongoing_by_label = {}
        for label, card_list in self.cards_by_label.items():
            if (label not in self.product_label_names):
                continue

            ongoing_by_label[label] = []
            for card in card_list:
                if (card.list_id in self.ongoing_list_ids):
                    ongoing_by_label[label].append(card)

        return ongoing_by_label

    def ongoing_activities(self):
        ongoing_by_label = {}
        for label, card_list in self.cards_by_label.items():
            if (label not in self.task_label_names):
                continue

            ongoing_by_label[label] = []
            for card in card_list:
                if (card.list_id in self.ongoing_list_ids):
                    ongoing_by_label[label].append(card)

        return ongoing_by_label

    def epics(self):
        ongoing_by_label = {}
        for label, card_list in self.cards_by_label.items():
            if (label not in self.epic_label_names):
                continue

            ongoing_by_label[label] = []
            for card in card_list:
                if (card.list_id in self.ongoing_list_ids):
                    ongoing_by_label[label].append(card)

        return ongoing_by_label


def sort_cards_by_due(card):
    """ Sorting key function for sorting a list of cards by their due date. """
    if card.due:
        return card.due
    else:
        return ''


def add_card_types(card_list, accepted_labels):
    """
    Adds a new field named "type" to each card in the given list. The type will be a list
    of all label names in that card that appear in the list of provided acceptable labels.
    If the card has no labels or none match, the type field will be an empty list.
    """
    for c in card_list:
        card_types = []
        if c.labels:
            card_types = [l.name for l in c.labels if l.name in accepted_labels]
        c.types = card_types
