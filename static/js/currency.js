function format_currency(amount, currencyCode = 'MXN', withCode = false, withSymbol = false) {
  const localeMap = {
    MXN: 'es-MX',
    USD: 'en-US',
    EUR: 'de-DE',
    GBP: 'en-GB',
    JPY: 'ja-JP',
    BRL: 'pt-BR',
    ARS: 'es-AR',
    CLP: 'es-CL',
    FRF: 'fr-FR',
  };

  const locale = localeMap[currencyCode] || 'en-US';

  //Get the number formatted as text
  const formattedNumber = new Intl.NumberFormat(locale, {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);

  //Get symbol if required
  let symbol = '';
  if (withSymbol) {
    symbol = new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
      .formatToParts(amount)
      .find(part => part.type === 'currency')?.value || '';
  }

  //Build results
  let result = formattedNumber;
  if (withSymbol) result = symbol + ' ' + result;
  if (withCode) result += ' ' + currencyCode;

  return result.trim();
}