/*
Which app genres contain the most under- and over-privileges?
*/

create view over_permissions
as
select v.appID, v.versionId, -- Version
    group_concat(trim(ovp_p.Name),';') as over_permissions, -- extra permission 
    count(1) as over_permission_count
from Version as v
left outer join OverPermission ovp on v.versionId = ovp.versionid
inner join Permission ovp_p on ovp.PermissionId = ovp_p.PermissionId
group by v.appId, v.VersionId


select app.categories, up.* 
from under_permissions as up
inner join AppData as app on up.appid=app.appid
inner join (
    select appid, max(versionid) as versionid 
    from under_permissions
    group by appid ) as max_v
on up.appid=max_v.appid and up.versionid=max_v.versionid    

create view app_perms as 
select app.categories, app.appid, 
    under.versionid as under_versionId, under.under_permissions, under_permission_count,
    overp.versionid as over_versionId, overp.over_permissions, overp.over_permission_count
from AppData as app
left join (
    select up.* 
    from under_permissions as up
    inner join AppData as app on up.appid=app.appid
    inner join (
        select appid, max(versionid) as versionid 
        from under_permissions
        group by appid ) as max_v
        on up.appid=max_v.appid and up.versionid=max_v.versionid) as under
            on app.appid = under.appid
left join (
    select up.* 
    from over_permissions as up
    inner join AppData as app on up.appid=app.appid
    inner join (
        select appid, max(versionid) as versionid 
        from over_permissions
        group by appid ) as max_v
        on up.appid=max_v.appid and up.versionid=max_v.versionid) as overp
            on app.appid = overp.appid
                                



select appdata.categories, count(distinct appdata.appid) as apps, sum(perms_set.over_permission_count) as over_count, sum(perms_set.under_permission_count) as under_count
--select perms_set.*
from (
    select overages.*, underages.under_permissions, underages.under_permission_count
    from (
        select v.appID, v.versionId, -- Version
            group_concat(trim(ovp_p.Name),';') as over_permissions, -- extra permission 
            count(1) as over_permission_count
        from Version as v
        left outer join OverPermission ovp on v.versionId = ovp.versionid
        inner join Permission ovp_p on ovp.PermissionId = ovp_p.PermissionId
        group by v.appId, v.VersionId ) as overages
    full outer join (
        select v.appID, v.versionId, -- Version
            group_concat(trim(ovp_p.Name),';') as under_permissions, -- extra permission 
            count(1) as under_permission_count
        from Version as v
        left outer join UnderPermission ovp on v.versionId = ovp.versionid
        inner join Permission ovp_p on ovp.PermissionId = ovp_p.PermissionId
        group by v.appId, v.VersionId ) as underages
    on 
        overages.appId = underages.appId
    and overages.versionId = underages.versionId ) as perms_set
left outer join appdata 
on perms_set.appid= appdata.appid
group by appdata.categories

/*
Is there is a correlation between an app’s security and quality metrics?

Feature Selection based on AndroriskAnalysis.pdf
*/
select appid, name, versionid, categories, fuzzy_risk, ncloc,complexity
from (
    select 
        v.appID, v.versionId, -- Version
        app.name,categories,
        round(vuln.fuzzy_risk,2) as fuzzy_risk, -- Vulnerability
        code.classes, code.functions, code.comment_lines, code.ncloc, code.lines, -- code metadata
        code.complexity, code.class_complexity, code.function_complexity, --code complexity
        code.blocker_violations, code.critical_violations, code.major_violations, code.minor_violations
    from Version as v
    left outer join Vulnerability vuln on v.versionId = vuln.versionId
    left outer join CodingStandard code on v.versionId = code.VersionId
    left outer join appdata app on app.appid = v.appid
    where fuzzy_risk is not null
    and code.complexity is not null ) as data
order by appid, versionid    

/*
Is there is a correlation between the number of committers an app has, and its permission misuse?
*/

// This query is by users
select app.appId, app.categories, git.email, count(distinct commit_hash) as commits
from AppData as app
join GitHistory as git on app.appId = git.appId
group by app.appId, app.categories, git.email

// This query is by project
select app.appId, app.categories, count(distinct git.email) as committers
from AppData as app
join GitHistory as git on app.appId = git.appId
group by app.appId, app.categories

// Combine history and permissions
select appdata.appid, max(history.committers) as committers, sum(perms_set.over_permission_count) as over_count, sum(perms_set.under_permission_count) as under_count
from (
    select overages.*, underages.under_permissions, underages.under_permission_count
    from (
        select v.appID, v.versionId, -- Version
            group_concat(trim(ovp_p.Name),';') as over_permissions, -- extra permission 
            count(1) as over_permission_count
        from Version as v
        left outer join OverPermission ovp on v.versionId = ovp.versionid
        inner join Permission ovp_p on ovp.PermissionId = ovp_p.PermissionId
        group by v.appId, v.VersionId ) as overages
    full outer join (
        select v.appID, v.versionId, -- Version
            group_concat(trim(ovp_p.Name),';') as under_permissions, -- extra permission 
            count(1) as under_permission_count
        from Version as v
        left outer join UnderPermission ovp on v.versionId = ovp.versionid
        inner join Permission ovp_p on ovp.PermissionId = ovp_p.PermissionId
        group by v.appId, v.VersionId ) as underages
    on 
        overages.appId = underages.appId
    and overages.versionId = underages.versionId ) as perms_set
left outer join appdata on perms_set.appid= appdata.appid
left outer join (
    select app.appId, app.categories, count(distinct git.email) as committers
    from AppData as app
    join GitHistory as git on app.appId = git.appId
    group by app.appId, app.categories ) as history on appdata.appid = history.appid
group by appdata.appid

/*
Put everything together
*/
create view result_set 
as
select appdata.categories,appdata.appid, git.committers, ver.versionid,    
    overages.over_permissions, over_permission_count,
    underages.under_permissions, underages.under_permission_count,
    round(vuln.fuzzy_risk,0) as fuzzy_risk,
    code.classes, code.functions, code.comment_lines, code.ncloc, code.lines, -- code metadata
    code.complexity, code.class_complexity, code.function_complexity, --code complexity
    code.blocker_violations, code.critical_violations, code.major_violations, code.minor_violations
from appdata
left join Version as ver on appdata.appid = ver.versionID

-- Find project committer count
left join (select appid, count(distinct email) as committers from GitHistory group by appid) as git
    on git.appid = appdata.appid

-- Find extra permissions
left join (
        select v.appID, v.versionId, -- Version
            group_concat(trim(ovp_p.Name),';') as over_permissions, -- extra permission 
            count(1) as over_permission_count
        from Version as v
        left outer join OverPermission ovp on v.versionId = ovp.versionid
        inner join Permission ovp_p on ovp.PermissionId = ovp_p.PermissionId
        group by v.appId, v.VersionId ) as overages
    on appdata.appid = overages.appid and ver.versionID = overages.versionID

-- Find missing permissions
left join (
        select v.appID, v.versionId, -- Version
            group_concat(trim(ovp_p.Name),';') as under_permissions, -- missing permission 
            count(1) as under_permission_count
        from Version as v
        left outer join UnderPermission ovp on v.versionId = ovp.versionid
        inner join Permission ovp_p on ovp.PermissionId = ovp_p.PermissionId
        group by v.appId, v.VersionId ) as underages
    on appdata.appid = underages.appid and ver.versionid = underages.versionid

-- Find Androrisk results
left outer join Vulnerability vuln on ver.versionId = vuln.versionId

-- Find sonar results
left outer join CodingStandard code on ver.versionId = code.VersionId
order by appdata.appid, ver.versionID