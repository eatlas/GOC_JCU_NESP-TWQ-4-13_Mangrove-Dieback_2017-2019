<#assign baseURL="https://nextcloud.eatlas.org.au/apps/files_sharing/publicpreview/kW4wHB5ebFoYgoQ?file=">

<table>
  <tr>
    <th>2017 Survey</th>
    <th>2019 Survey</th>
    <th>Shore_FID</th>
    <th>Shore_Mang</th>
    <th>Density</th>
    <th>Type</th>
    <th>Dieback</th>
  </tr>
  <#list features as feature>
  <tr>
    <#-- 2017 Survey Thumbnail and Image URL -->
    <#assign divShort2017=feature["DivShort"]>
    <#assign image2017=feature["2017_Image"]>
    <#assign thumb2017="${baseURL}/images/2017_Shoreline/${divShort2017}/${image2017}&x=256&y=144">
    <#assign full2017="${baseURL}/images/2017_Shoreline/${divShort2017}/${image2017}">
    
    <#-- 2019 Survey Thumbnail and Image URL -->
    <#assign divShort2019=feature["DivShort"]>
    <#assign image2019=feature["2019_Image"]>
    <#assign thumb2019="${baseURL}/images/2019_Shoreline/${divShort2019}/${image2019}&x=256&y=144">
    <#assign full2019="${baseURL}/images/2019_Shoreline/${divShort2019}/${image2019}">

    <#-- Check if 2017 Image is available and display thumbnail or placeholder -->
    <#if image2017??>
      <td>
        <a href="${full2017}" target="_blank">
          <img src="${thumb2017}" alt="2017 Survey Image" width="256" height="144">
        </a>
      </td>
    <#else>
      <td>No 2017 Image Available</td>
    </#if>
    
    <#-- Check if 2019 Image is available and display thumbnail or placeholder -->
    <#if image2019??>
      <td>
        <a href="${full2019}" target="_blank">
          <img src="${thumb2019}" alt="2019 Survey Image" width="256" height="144">
        </a>
      </td>
    <#else>
      <td>No 2019 Image Available</td>
    </#if>

    <#-- Additional attributes -->
    <td>${feature.Shore_FID?html}</td>
    <td>${feature.Shore_Mang?html}</td>
    <td>${feature.Density?html}</td>
    <td>${feature.Type?html}</td>
    <td>${feature.Dieback?html}</td>
  </tr>
  </#list>
</table>
