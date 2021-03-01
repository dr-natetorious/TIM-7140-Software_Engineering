/*
    Get Version Coding Standards
*/
select 
    v.appID, v.versionId, -- Version
    round(vuln.fuzzy_risk,2) as fuzzy_risk, -- Vulnerability
    code.classes, code.functions, code.comment_lines, code.ncloc, code.lines, -- code metadata
    code.complexity, code.class_complexity, code.function_complexity, --code complexity
    code.blocker_violations, code.critical_violations, code.major_violations, code.minor_violations
from Version as v
left outer join Vulnerability vuln on v.versionId = vuln.versionId
left outer join CodingStandard code on v.versionId = code.VersionId
where v.appId=1

/*
    Get extra permissions
*/
select overages.*, underages.under_permissions
from (
    select v.appID, v.versionId, -- Version
        group_concat(trim(ovp_p.Name),';') as over_permissions -- extra permission 
    from Version as v
    left outer join OverPermission ovp on v.versionId = ovp.versionid
    inner join Permission ovp_p on ovp.PermissionId = ovp_p.PermissionId
    group by v.appId, v.VersionId ) as overages
full outer join (
    select v.appID, v.versionId, -- Version
        group_concat(trim(ovp_p.Name),';') as under_permissions -- extra permission 
    from Version as v
    left outer join OverPermission ovp on v.versionId = ovp.versionid
    inner join Permission ovp_p on ovp.PermissionId = ovp_p.PermissionId
    group by v.appId, v.VersionId ) as underages
on 
    overages.appId = underages.appId
    and overages.versionId = underages.versionId

/*
    App Change History
*/
select app.appId, app.name, app.auto_name, app.categories, git.commit_hash, git.author, git.email, git.time, git.summary
from AppData as app
left join GitHistory as git on app.appId = git.appId
