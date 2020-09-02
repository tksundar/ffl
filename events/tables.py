#
#
# class RegTable(django_tables2.Table):
#     class Meta:
#         model = Registration
#         exclude = ('id', 'email', 'mobile')
#
#
# class DeletedRegistrationsTable(django_tables2.Table):
#     class Meta:
#         model = Registration
#         exclude = ('id', 'email', 'mobile', 'arrival_date', 'departure_date', 'pickup_reqd', 'special_req',
#                    'extended_tour', 'mode_of_travel',)
