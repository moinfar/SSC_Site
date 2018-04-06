from django import forms

from transactions.models import PriceGroup, DiscountCode


class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = PriceGroup
        fields = ['group_identifier', 'payment_amount', 'capacity', 'discount_codes']

    discount_codes = forms.CharField(required=False)

    def __init__(self, instance=None, **kwargs):
        super().__init__(instance=instance, **kwargs)
        if instance:
            discount_codes = instance.discount_codes.all()
            self.fields['discount_codes'].initial = ', '.join(
                ['{} {}% {}'.format(x.code, x.discount_percentage, x.capacity) for x in
                 discount_codes])

    def clean_discount_codes(self):

        discount_codes = self.cleaned_data.get(
            'discount_codes') if 'discount_codes' in self.changed_data else None
        if not discount_codes:
            return []
        discount_codes = discount_codes.split(',')
        out = {}
        error = False
        for discount_code in discount_codes:
            if not discount_code:
                continue
            # Trying to parse the input!
            splitted = discount_code.split()
            if len(splitted) == 0:
                continue
            error = True
            try:
                if len(splitted) == 3:
                    if not splitted[1].endswith('%'):
                        break
                    percent = int(splitted[1][:-1])
                elif len(splitted) == 4:
                    if splitted[2] == '%':
                        splitted[2], splitted[3] = splitted[3], splitted[2]
                    else:
                        break
                    percent = int(splitted[1])
                else:
                    break
                capacity = int(splitted[2])
            except ValueError:
                break

            if capacity < -1 or percent < 0 or percent > 100:
                break

            error = False
            if splitted[0] in out:
                self.add_error('discount_codes', 'discount codes must be unique')
                return
            out[splitted[0]] = [percent, capacity]

        if error:
            self.add_error('discount_codes', 'invalid discount code format for "{}"'
                                             '; You should enter comma-separated codes each in '
                                             'format "<code> <discount_percentage>% <capacity>"; '
                                             'For example: "CDJXD 40% 23" or "CD -1 10%" '.format(
                discount_code))
        return out

    def save(self, commit=True):
        ret = super().save(commit=commit)
        if commit:
            discount_codes = list(self.instance.discount_codes.all())
            form_discount_codes = self.cleaned_data['discount_codes']
            if not form_discount_codes:
                return ret
            for discount_code in discount_codes:
                l = form_discount_codes.get(discount_code.code)
                if not l:
                    discount_code.delete()
                else:
                    discount_code.discount_percentage = l[0]
                    discount_code.capacity = l[1]
                    discount_code.save()
                    form_discount_codes.pop(discount_code.code)
            for code, l in form_discount_codes.items():
                DiscountCode.objects.create(price_group=self.instance, code=code,
                                            discount_percentage=l[0], capacity=l[1])
        return ret
