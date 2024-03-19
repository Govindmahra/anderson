select = {
    'church_name': 'span.church_name ::text',
    'district': 'span.district ::text',
    'physical_address': 'span.physical_address ::text',
    'mailing_address': 'span.mailing_address ::text',
    'clergy_link': 'p > a ::attr(href)',
    'clergy_name': 'span.clergy_name ::text',
    'email': 'p > a.geo-address ::attr(href)',
    'phone': 'span.phone > a ::text',
}

select2 = {
    'link': 'a ::attr(href)',
    'church_url': 'h5.entry-title > a ::attr(href)',
    'church_name': 'div.headline > h2 ::text',
    'church_website': 'span.cmsms_category > a ::attr(href)',
    'church_phone': 'header.entry-header > span[itemprop="telephone"] ::text',
    'church_address': 'header.entry-header > div[itemprop="address"] > span ::text',
}
select3 = {
    'last_page_number': 'a.page-link ::attr(data-page)',
    'name': 'a[title="Provider Title"] ::text',
    'locations': '#locations-list > div',
    'address': 'span[itemprop="streetAddress"] ::text',
    'country': 'span[itemprop="addressCountry"] ::text',
    'City': 'span[itemprop="addressLocality"] ::text',
    'state': 'span[itemprop="addressRegion"] ::text',
    'zip_code': 'span[itemprop="postalCode"] ::text',
    'phone': 'a[itemprop="telephone"] ::text',
    'website': 'a[title="Visit website"] ::attr(href)',
    'linkedin': 'a[data-type="linkedin"] ::attr(href)',
}
