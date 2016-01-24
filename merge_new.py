#!/usr/bin/python

import os, subprocess, shlex
import re
import yaml
import httplib2
import json
import argparse
import time
import tarfile



def get_args():
    '''This function parses and return arguments passed in'''
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description='Script Do deployment process automated')
    # Add arguments
    parser.add_argument(
        '-a', '--app', type=str, help='Application Name', required=False)
    parser.add_argument(
        '-e', '--env', type=str, help='Application ENV type', required=False)
    parser.add_argument(
        '-f', '--file', type=str, help='YAML File', required=False, default=None)
    parser.add_argument(
        '--bypass', type=bool, help='Bypass SVN', required=False, default=None)
    # Array for all arguments passed to script
    args = parser.parse_args()
    #print type(args)
    # Assign args to variables
    app = args.app
    env = args.env
    file = args.file
    svn_bypass = args.bypass
    # Return all variable values
    return (app, env, file, svn_bypass)

def __read_bash_env():
    #app = os.environ.get('version')
    #env = os.environ.get('env')

   # print 'PROJECT NAME: '+os.environ.get('projectname')
    env_dict['app'] = os.environ.get('projectname')
    env_dict['env'] = os.environ.get('env')
    env_dict['svnroot'] = os.environ.get('svnroot')
    env_dict['envname'] = os.environ.get('envname')
    env_dict['version'] = os.environ.get('version')
    env_dict['translationsversion'] = os.environ.get('translationsversion')
    env_dict['jira'] = os.environ.get('jira')
    env_dict['deploy'] = os.environ.get('deploy')

    return env_dict

def __runBash(cmd):
    formatted_cmd = shlex.split(cmd)
#    print formatted_cmd
    try:
        p = subprocess.Popen(formatted_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.communicate()
    except OSError as exception:
        raise

def __dir_test_and_create(path):
    #print 'Creating missing locations'
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
            else:
                print "\nBE CAREFUL! Directory %s already exists." % path

def __yaml_to_dict(fl):
#    print 'Converting from YAML to DICT OBJ to FILE: '+fl
    with open(fl, 'r') as YAML:
        d = yaml.load(YAML)
        return d

def __folder_struct():
 #   print 'Creating Directories  Necessary Stracture'
    file = tmp_workspace['merge']
    file = file+'/'+toDay

    file_path = tmp_workspace['svn']+'/'+'prod_templates'+'/'+'folder_tree.yaml'
    d = __yaml_to_dict(file_path)
    for i in d:
        new_pkg_dirs = file+'/'+i
#        print new_pkg_dirs
        __dir_test_and_create(new_pkg_dirs)

def __svn_checkout(envname):

    path = ''
    svn_url = ' http://svn.sp.vodafone.com/svn/superstore/'
    SVN = 'svn co --username contdisc.backup --password contdisc.backup --no-auth-cache'
    if envname == 'apache':
        path_fe = SVN+' '+svn_url+envname+'/configuration/apache/discover/'
        path_prdstg = path_fe+'LIVE_SMHS_SSP_STG/htdocs.shopfeiws/ssp'
        path_prod = path_fe+'LIVE_SMHS_SSP/htdocs.shopfeiws/ssp'

        cmd1 = path_prdstg+' '+tmp_workspace['svn']+'/'+envname+'/LIVE_SMHS_SSP_STG/'
        cmd2 = path_prod+' '+tmp_workspace['svn']+'/'+envname+'/LIVE_SMHS_SSP/'
        __runBash(cmd1)
        __runBash(cmd2)
    elif envname == 'conf':
        path = env_dict['svnroot']+'/'+envname+'/'+env_dict['svnroot']+'_'+env_dict['envname']+' '+tmp_workspace['svn']+'/'+envname+'/'
        __runBash(SVN+svn_url+path)
    else:
        path = env_dict['svnroot']+'/'+envname+' '+tmp_workspace['svn']+'/'+envname
        __runBash(SVN+svn_url+path)


def __extract_tarfile(file, target):

        try:
            tarball = tarfile.open(file, mode='r:gz')
        except Exception:
            print("Response not a valid tar file.")
            print("Clone failed")
            return
        tarball.extractall(target)
        print("Clone successful")

def __prepare_downloadBuild():

    import base64
    _url_build = "https://buildteam.dct.vodafone.com/releases/"
    smhs = '/com/vodafone/global/SMHS/SMHS/'
    ddp = '/com/vodafone/service/start/ddp/'
    auth = "puppet:p@pus@.DevOps#2014"
    version = env_dict['version']
#    print version
    auth = base64.encodestring( auth )
    RELEASE_NAME=''
    buildType = re.match(r'[\d.]+[-]([A-Z]{2,4})\d+',version)
    if env_dict['app'] == 'ssp':
        _url_build = _url_build+buildType.group(1)+smhs
        RELEASE_NAME = 'SMHS-'+version+'.tar.gz'
        target_folder = 'SMHS-'+version
#        _url_build = _url_build+version+'/'+RELEASE_NAME
#        print 'RELEASE_NAME: '+RELEASE_NAME
#        print target_folder
#        print _url_build
        __downloadBuild(target_folder, _url_build,RELEASE_NAME, auth, version)
    if env_dict['app'] == 'ddp':
        _url_build = _url_build+buildType.group(1)+ddp
        RELEASE_NAME = 'ddp-'+version+'.tar.gz'
        target_folder = 'ddp-'+version
#        _url_build = _url_build+version+'/'+RELEASE_NAME
#        print 'RELEASE_NAME: '+RELEASE_NAME
#        print target_folder
#        print _url_build
        __downloadBuild(target_folder, _url_build,RELEASE_NAME, auth, version)

def __downloadBuild(target_folder, _url_build, RELEASE_NAME, auth, version):

    import urllib2
    url = _url_build+version+'/'+RELEASE_NAME

    print url
    headers = { 'Authorization' : 'Basic ' + auth }
    dest_file = tmp_workspace['build']+'/'+RELEASE_NAME
    req = urllib2.Request( url, 'GET', headers = headers )
    u = urllib2.urlopen(req)

    f = open(dest_file, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (dest_file, file_size)
    os.system('cls')
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

    if os.path.isfile(tmp_workspace['build']+'/'+RELEASE_NAME):
        print tmp_workspace['build']+'/'+RELEASE_NAME, tmp_workspace['build']+'/'+target_folder
        __extract_tarfile(tmp_workspace['build']+'/'+RELEASE_NAME, tmp_workspace['build']+'/'+target_folder)

def __file_modify_to_pupet_erb_format(src_file, dst_file):
    str1 = "<%= @hiera_hash['"
    str2 = "] || fail('Missing property value: "
    str3 = "') %>"
    if os.path.isfile(src_file):
        with open(dst_file,'w') as wf:
            with open(src_file, 'r') as f:
                for line in f:
                    if not (line == '\n' or line.startswith('#')):
                        match = line.split('=',2)
                        #    print match[0]
                        L = str(match[0])+'='+str(str1)+str(match[0])+str(str2)+str(match[0])+str(str3)
                        wf.write(L)
                        wf.write("\n")
                    else:
                        wf.write(line)
#                        wf.write("\n")

def __Copy_files_from_build(src_pth, dst_path):


    cmd = 'cp '+src_pth+' '+dst_path
#    print cmd
    __runBash(cmd)


def __build_fe_resource():
    __svn_checkout('apache')
    src_res_fe = tmp_workspace['build']+'/SMHS-'+env_dict['version']+'/config/ssp'
    dst_res_fe_stg = tmp_workspace['svn']+'/apache/LIVE_SMHS_SSP_STG/'+toDay+'/'
    dst_res_fe = tmp_workspace['svn']+'/apache/LIVE_SMHS_SSP/'+toDay+'/'
    cmd1 = 'cp -R '+src_res_fe+' '+dst_res_fe
    cmd2 = 'cp -R '+src_res_fe+' '+dst_res_fe_stg
    __runBash(cmd1)
    __runBash(cmd2)

def __do_Merge_operation():
    print 'Do merge operation'
    __copy_from_templats()
    #global src
    if env_dict['app'] == 'ddp':
        t = 'ddp-'
    if env_dict['app'] == 'ssp':
        t = 'SMHS-'
    print 'Lets format the dynamic files'
    property_tamplate = tmp_workspace['svn']+'/'+'prod_templates/app.properties'
    src = tmp_workspace['build']+'/'+t+env_dict['version']+'/config/'
    dst = tmp_workspace['merge']+'/'+toDay
    if os.path.isfile(property_tamplate):
        with open(property_tamplate, 'r') as f:
            for i in f:
                str = i.split('\n')
                pth_erb = src+str[0]+'.erb'
                pth = src+str[0]
                if os.path.isfile(pth):
                    pth = src+str[0]
                    dest = dst+'/'+str[0]+'.erb'
                    if env_dict['app'] == 'ddp':
#                        print pth
                        __file_modify_to_pupet_erb_format(pth, dest)
                    elif env_dict['app'] == 'ssp':
                        __Copy_files_from_build(pth, dest)
                elif os.path.isfile(pth_erb):
                    pth = src+str[0]+'.erb'
                    dest = dst+'/'+str[0]+'.erb'
                    if env_dict['app'] == 'ddp':
 #                       print pth
                        __file_modify_to_pupet_erb_format(pth, dest)
                    elif env_dict['app'] == 'ssp':
                        __Copy_files_from_build(pth, dest)

                elif not os.path.isfile(src+str[0]):
                    pth = src+str[0]
                    dest = dst+'/'+str[0]+'.erb'
                    cmd = 'touch '+dest
                    __runBash(cmd)

    if env_dict['app'] == 'ssp':
        src_config = src+'/ssp/res/css/img/'
        resource_dest = dst = tmp_workspace['merge']+'/'+toDay+'/ssp/res/css/'
        cmd = 'cp -R '+src_config+' '+resource_dest
        __runBash(cmd)
        __build_fe_resource()

def __copy_from_templats():
    src = tmp_workspace['svn']+'/'+'prod_templates/config_default'
    dst = tmp_workspace['merge']+'/'+toDay
    for filename in os.listdir(src):
        cmd = 'cp -R '+src+'/'+filename+' '+dst+'/'
#        print cmd
        __runBash(cmd)

def __setEnv():
    print 'START SETTING ENV'
    tmp_loc = '/home/gmohapat/data/'
    tmp_workspace['svn'] = tmp_loc+str(env_dict['svnroot'])+'/'+'svn'
    tmp_workspace['build'] = tmp_loc+str(env_dict['svnroot'])+'/'+'build'
    tmp_workspace['merge'] = tmp_loc+str(env_dict['svnroot'])+'/'+'merge'
    tmp_workspace['conf'] = tmp_loc+str(env_dict['svnroot'])+'/'+'conf'


    for l in tmp_workspace:
        #print l+'======>'+tmp_workspace[l]

        __dir_test_and_create(tmp_workspace[l])


class REMatcher(object):
    def __init__(self, matchstring):
        self.matchstring = matchstring

    def match(self,regexp):
        self.rematch = re.match(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self,i):
        return self.rematch.group(i)



def main():
    global env_dict
    global tmp_workspace
    global args
    global project_svn_loc
    global toDay
    global common_yaml_dict
    global app_yaml_dict
    global RELEASE_NAME


    project_svn_loc = ('conf','prod_templates','puppet_data')
    env_dict = {}
    tmp_workspace = {}
    common_yaml_dict = {}
    app_yaml_dict = {}
    RELEASE_NAME = ''

#    print len(env_dict)
    '''
    Main program
    '''
    '''env_dict = __read_bash_env()
    print str(env_dict['deploy'])

#    if env_dict['deploy'] in env_dict:
    if str(env_dict['deploy']) == 'jenkins':
            print 'read bash'
            env_dict = __read_bash_env()
            for i in env_dict:
            #    print i
                __setEnv()
                for s in project_svn_loc:
                    print 'hi'
    #               __svn_checkout(s)
    else:
        if not str(env_dict['deploy']) == 'jenkins':
            print 'Deploy type: '+str(env_dict['deploy'])
            print "Should not here"'''

    args = get_args()
    print args
    env_dict['app'] = args[0]
    env_dict['env'] = args[1]
    if args[0] == 'ssp':
        env_dict['svnroot'] = 'smhs'
        env_dict['envname'] = 'SSP'
    elif args[0] == 'ddp':
        env_dict['svnroot'] = 'ddp'
        env_dict['envname'] = 'PROD'

    __setEnv()

    print 'Checking SVN'
    for s in project_svn_loc:
#        print s
        __svn_checkout(s)

    file_path = tmp_workspace['svn']+'/'+'puppet_data'
    common_yaml_dict = __yaml_to_dict(file_path+'/'+env_dict['svnroot']+'_'+env_dict['envname']+'.common.yaml')
    app_yaml_dict = __yaml_to_dict(file_path+'/'+env_dict['svnroot']+'_'+env_dict['envname']+'.yaml')
    env_dict['version'] = common_yaml_dict['version']

    toDay = time.strftime('%Y%m%d')
    toDay = 'config'+'_'+env_dict['version']+'_'+toDay
    __folder_struct()
    __prepare_downloadBuild()
    __do_Merge_operation()

if __name__ == "__main__":
    main()

