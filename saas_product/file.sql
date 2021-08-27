Update mail_template set body_html='<div style="margin: 0px; padding: 0px;">
    <p style="margin: 0px; padding: 0px; font-size: 12px;">
        Hello,
        <br/><br/>
        % set transaction = object.get_portal_last_transaction()
        Your order <strong>${object.name}</strong> amounting in <strong>${format_amount(object.amount_total, object.currency_id)}</strong>
        % if object.state == ''sale'' or (transaction and transaction.state in (''done'', ''authorized'')) :
            has been confirmed.<br/>
            Thank you for your trust!
        % elif transaction and transaction.state == ''pending'' :
            is pending. It will be confirmed when the payment is received.
            % if object.reference:
                Your payment reference is <strong>${object.reference}</strong>.
            % endif
        % endif
        <br/><br/>
        Do not hesitate to contact us if you have any questions.
        <br/><br/>
        % if object.website_id:
            <table width="100%" style="color: #454748; font-size: 12px; border-collapse: collapse;">
                <tr style="border-bottom: 2px solid #dee2e6;">
                    <td width="18%"><strong>Products</strong></td>
                    <td></td>
                    <td><strong>Quantity</strong></td>
                    <td width="10%" align="center"><strong>Price</strong></td>
                </tr>
                % for line in object.order_line:
                    % if not line.is_delivery:
                        <tr >
                            % if line.display_type == ''line_section'':
                                <td colspan="4"><strong>${line.name}</strong></td>
                            % elif line.display_type == ''line_note'':
                                <td colspan="4"><i>${line.name}</i></td>
                            % else:
                                <td style="width: 150px;">
                                    <img src="/web/image/product.product/${line.product_id.id}/image_128" style="width: 64px; height: 64px; object-fit: contain;" alt="Product image"></img>
                                </td>
                                <td align="left">${line.product_id.name}</td>
                                <td>${line.product_uom_qty}</td>
                                % if object.user_id.has_group(''account.group_show_line_subtotals_tax_excluded''):
                                    <td align="right">${format_amount(line.price_reduce_taxexcl, object.currency_id)}</td>
                                % endif
                                % if object.user_id.has_group(''account.group_show_line_subtotals_tax_included''):
                                    <td align="right">${format_amount(line.price_reduce_taxinc, object.currency_id)}</td>
                                % endif
                            % endif
                        </tr>
                    % endif
                % endfor
            </table>
            <table width="40%" style="color: #454748; font-size: 12px; border-spacing: 0px 4px;" align="right">
                % if object.carrier_id:
                    <tr>
                        <td style="border-top: 1px solid #dee2e6;" align="right"><strong>Delivery:</strong></td>
                        <td style="border-top: 1px solid #dee2e6;" align="right">${format_amount(object.amount_delivery, object.currency_id)}</td>
                    </tr>
                    <tr>
                        <td width="30%" align="right"><strong>SubTotal:</strong></td>
                        <td align="right">${format_amount(object.amount_untaxed, object.currency_id)}</td>
                    </tr>
                % else:
                    <tr>
                        <td style="border-top: 1px solid #dee2e6;" width="30%" align="right"><strong>SubTotal:</strong></td>
                        <td style="border-top: 1px solid #dee2e6;" align="right">${format_amount(object.amount_untaxed, object.currency_id)}</td>
                    </tr>
                % endif
                <tr>
                    <td align="right"><strong>Taxes:</strong></td>
                    <td align="right">${format_amount(object.amount_tax, object.currency_id)}</td>
                </tr>
                <tr>
                    <td style="border-top: 1px solid #dee2e6;" align="right"><strong>Total:</strong></td>
                    <td style="border-top: 1px solid #dee2e6;" align="right">${format_amount(object.amount_total, object.currency_id)}</td>
                </tr>
            </table>
            <br/>
            <table width="100%" style="color: #454748; font-size: 12px;">
                % if object.partner_invoice_id:
                    <tr>
                        <td style="padding-top: 10px;">
                            <strong>Bill to:</strong>
                            ${object.partner_invoice_id.street or ''''}
                            ${object.partner_invoice_id.city or ''''}
                            ${object.partner_invoice_id.state_id.name or ''''}
                            ${object.partner_invoice_id.zip or ''''}
                            ${object.partner_invoice_id.country_id.name or ''''}
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <strong>Payment Method:</strong>
                            % if transaction.payment_token_id:
                                ${transaction.payment_token_id.name}
                            % else:
                                ${transaction.acquirer_id.name}
                            % endif
                             (${format_amount(transaction.amount, object.currency_id)})
                        </td>
                    </tr>
                % endif
                % if object.partner_shipping_id and not object.only_services:
                    <tr>
                        <td>
                            <br/>
                            <strong>Ship to:</strong>
                            ${object.partner_shipping_id.street or ''''}
                            ${object.partner_shipping_id.city or ''''}
                            ${object.partner_shipping_id.state_id.name or ''''}
                            ${object.partner_shipping_id.zip or ''''}
                            ${object.partner_shipping_id.country_id.name or ''''}
                        </td>
                    </tr>
                    % if object.carrier_id:
                        <tr>
                            <td>
                                <strong>Shipping Method:</strong>
                                ${object.carrier_id.name}
                                % if object.carrier_id.fixed_price == 0.0:
                                    (Free)
                                % else:
                                    (${format_amount(object.carrier_id.fixed_price, object.currency_id)})
                                % endif
                            </td>
                        </tr>
                    % endif
                % endif
            </table>
        % endif
    </p>
</div>' where name='Sales Order: Confirmation Email';


