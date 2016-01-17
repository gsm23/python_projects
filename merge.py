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


    svn_url = ' http://svn.sp.vodafone.com/svn/superstore/'
    SVN = 'svn co --username contdisc.backup --password contdisc.backup --no-auth-cache'
    if envname == 'apache':
        path = envname
    elif envname == 'conf':
        path = env_dict['svnroot']+'/'+envname+'/'+env_dict['svnroot']+'_'+env_dict['envname']+' '+tmp_workspace['svn']+'/'+envname+'/'
    else:
        path = env_dict['svnroot']+'/'+envname+' '+tmp_workspace['svn']+'/'+envname
    cmd = SVN+svn_url+path
#    __runBash(cmd)

def __extract_tarfile(file, target):

        try:
            tarball = tarfile.open(file, mode='r:gz')
        except Exception:
            print("Response not a valid tar file.")
            print("Clone failed")
            return
        tarball.extractall(target)
        print("Clone successful")

def __downloadBuild():
    _url_build = "https://buildteam.dct.vodafone.com/releases/"
    smhs = '/com/vodafone/global/SMHS/SMHS/'
    ddp = '/com/vodafone/service/start/ddp/'
    auth = "puppet:p@pus@.DevOps#2014"
    version = env_dict['version']
    #print version
    RELEASE_NAME=''
    buildType = re.match(r'[\d.]+[-]([A-Z]{2,4})\d+',version)
    if env_dict['app'] == 'ssp':
        _url_build = _url_build+buildType.group(1)+smhs
        RELEASE_NAME = 'SMHS-'+version+'.tar.gz'
        target_folder = 'SMHS-'+version
    if env_dict['app'] == 'ddp':
        _url_build = _url_build+buildType.group(1)+ddp
        RELEASE_NAME = 'ddp-'+version+'.tar.gz'
        target_folder = 'ddp-'+version
        _url_build = _url_build+version+'/'+RELEASE_NAME
    import base64
    import httplib2
    h = httplib2.Http()
    auth = base64.encodestring( auth )
    headers = { 'Authorization' : 'Basic ' + auth }
    dest_file = tmp_workspace['build']+'/'+RELEASE_NAME
    '''try:
        resp, content = h.request( _url_build, 'GET', headers = headers )

        if resp.status == 200:
            with open(dest_file, 'wb') as fw:
                fw.write(content)
    except httplib2.ServerNotFoundError:
        print "Site is Down"'''

    __extract_tarfile(tmp_workspace['build']+'/'+RELEASE_NAME, tmp_workspace['build']+'/'+target_folder)

def __file_modify_to_pupet_erb_format():
    print 'FILE to modify to puppet erb format'

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

    #print src
    #print dst
    #print property_tamplate
    if os.path.isfile(property_tamplate):
        with open(property_tamplate, 'r') as f:
            for i in f:
                #print i
                str = i.split('\n')
                #print src+str[0]

                if os.path.isfile(src+str[0]):
                    pth = src+str[0]
                    print pth
                elif os.path.isfile(src+str[0]+'.erb'):
                    pth = src+str[0]+'.erb'
                    print pth


def __copy_from_templats():
    src = tmp_workspace['svn']+'/'+'prod_templates/config_default'
    dst = tmp_workspace['merge']+'/'+toDay
    for filename in os.listdir(src):
        cmd = 'cp -R '+src+'/'+filename+' '+dst+'/'
#       __runBash(cmd)

def __setEnv():

    tmp_loc = '/home/gmohapat/data/'
    tmp_workspace['svn'] = tmp_loc+env_dict['svnroot']+'/'+'svn'
    tmp_workspace['build'] = tmp_loc+env_dict['svnroot']+'/'+'build'
    tmp_workspace['merge'] = tmp_loc+env_dict['svnroot']+'/'+'merge'
    tmp_workspace['conf'] = tmp_loc+env_dict['svnroot']+'/'+'conf'

    for l in tmp_workspace:
        #print tmp_workspace[l]
        __dir_test_and_create(tmp_workspace[l])


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
    env_dict = __read_bash_env()
    if env_dict['deploy'] in env_dict:
        if env_dict['deploy'] == 'jenkins':
            env_dict = __read_bash_env()
            __setEnv()
            for s in project_svn_loc:
    #           print s
                __svn_checkout(s)
    else:
        if not env_dict['deploy'] == 'jenkins':
    #       print 'Deploy type: '+str(env_dict['deploy'])
            print "Should not here"
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
        for s in project_svn_loc:
      #      print s
            __svn_checkout(s)

        file_path = tmp_workspace['svn']+'/'+'puppet_data'
        common_yaml_dict = __yaml_to_dict(file_path+'/'+env_dict['svnroot']+'_'+env_dict['envname']+'.common.yaml')
        app_yaml_dict = __yaml_to_dict(file_path+'/'+env_dict['svnroot']+'_'+env_dict['envname']+'.yaml')
        env_dict['version'] = common_yaml_dict['version']

    toDay = time.strftime('%Y%m%d')
    toDay = 'config'+'_'+env_dict['version']+'_'+toDay
    __folder_struct()
    #__downloadBuild()
    __do_Merge_operation()


if __name__ == "__main__":
    main()

